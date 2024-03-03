package main

import (
	"bufio"
	"context"
	"flag"
	"fmt"
	"os"
	"strconv"
	"strings"
)

type NilsimsaRecord struct {
	name   string
	digest []int
}

type SimhashRecord struct {
	name   string
	digest uint64
}

func getNilsimsaRecords(nilsimsa Nilsimsa, filename string) ([]NilsimsaRecord, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	records := []NilsimsaRecord{}

	scanner := bufio.NewScanner(file)
	scanner.Scan() // header
	for scanner.Scan() {
		parts := strings.Split(scanner.Text(), ",")
		digest, err := nilsimsa.ConvertHexToInts(parts[1])
		if err != nil {
			return nil, err
		}
		name := parts[0]
		name = name[:len(name)-5] // without .html, mb comment it
		records = append(records, NilsimsaRecord{name: name, digest: digest})
	}

	if err := scanner.Err(); err != nil {
		return nil, err
	}

	return records, nil
}

func getSimhashRecords(filename string) ([]SimhashRecord, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	records := []SimhashRecord{}

	scanner := bufio.NewScanner(file)
	scanner.Scan() // header
	for scanner.Scan() {
		parts := strings.Split(scanner.Text(), ",")
		digest, err := strconv.ParseUint(parts[1], 10, 64)
		if err != nil {
			return nil, err
		}
		name := parts[0]
		name = name[:len(name)-5] // without .html, mb comment it
		records = append(records, SimhashRecord{name: name, digest: digest})
	}

	if err := scanner.Err(); err != nil {
		return nil, err
	}

	return records, nil
}

func nilsimsaBatch(ctx context.Context, filename1, filename2 string, ch chan<- string) error {
	if verbose {
		fmt.Printf("start %s -> %s\n", filename1, filename2)
	}
	nilsimsa := NewNilsimsa()

	records1, err := getNilsimsaRecords(nilsimsa, filename1)
	if err != nil {
		return err
	}

	select {
	case <-ctx.Done():
		return fmt.Errorf("canceled")
	default:
	}

	if filename1 == filename2 {
		for i, record1 := range records1 {
			for _, record2 := range records1[i+1:] {
				score := nilsimsa.Compare(record1.digest, record2.digest)
				if score < threshold {
					continue
				}
				// ch <- fmt.Sprintf("%s %s %d\n", record1.name, record2.name, score)
				ch <- fmt.Sprintf("%s,%s,%d,nilsimsa\n", record1.name, record2.name, score)
			}
		}
	} else {
		records2, err := getNilsimsaRecords(nilsimsa, filename2)
		if err != nil {
			return err
		}

		for _, record1 := range records1 {
			for _, record2 := range records2 {
				score := nilsimsa.Compare(record1.digest, record2.digest)
				if score < threshold {
					continue
				}
				// ch <- fmt.Sprintf("%s %s %d\n", record1.name, record2.name, score)
				ch <- fmt.Sprintf("%s,%s,%d,nilsimsa\n", record1.name, record2.name, score)
			}
		}
	}

	if verbose {
		fmt.Printf("finish %s -> %s\n", filename1, filename2)
	}
	return nil
}

func simhashBatch(ctx context.Context, filename1, filename2 string, ch chan<- string) error {
	if verbose {
		fmt.Printf("start %s -> %s\n", filename1, filename2)
	}

	records1, err := getSimhashRecords(filename1)
	if err != nil {
		return err
	}

	select {
	case <-ctx.Done():
		return fmt.Errorf("canceled")
	default:
	}

	simhash := NewSimhash()

	if filename1 == filename2 {
		for i, record1 := range records1 {
			for _, record2 := range records1[i+1:] {
				score := simhash.Compare(record1.digest, record2.digest)
				if score > threshold {
					continue
				}
				// ch <- fmt.Sprintf("%s %s %d\n", record1.name, record2.name, score)
				ch <- fmt.Sprintf("%s,%s,%d,simhash\n", record1.name, record2.name, score)
			}
		}
	} else {
		records2, err := getSimhashRecords(filename2)
		if err != nil {
			return err
		}

		for _, record1 := range records1 {
			for _, record2 := range records2 {
				score := simhash.Compare(record1.digest, record2.digest)
				if score > threshold {
					continue
				}
				// ch <- fmt.Sprintf("%s %s %d\n", record1.name, record2.name, score)
				ch <- fmt.Sprintf("%s,%s,%d,simhash\n", record1.name, record2.name, score)
			}
		}
	}

	if verbose {
		fmt.Printf("finish %s -> %s\n", filename1, filename2)
	}
	return nil
}

func saveResult(ctx context.Context, filename string, ch <-chan string) {
	f, err := os.Create(filename)
	if err != nil {
		panic(err)
	}
	defer f.Close()

	for {
		select {
		case <-ctx.Done():
			return
		case line := <-ch:
			_, err := f.WriteString(line)
			if err != nil {
				panic(err)
			}
		}
	}
}

var (
	algorithm      string
	threshold      int
	workers        int64
	filePrefix     string
	fileSuffix     string
	bathes         int
	resultFilename string
	verbose        bool
)

func init() {
	flag.StringVar(&algorithm, "algorithm", "nilsimsa", "algorithm name: nilsimsa | simhash")
	flag.IntVar(&threshold, "threshold", -1, "algorithm threshold")
	flag.Int64Var(&workers, "workers", 1, "number of simultaneously compared batches")
	flag.StringVar(&filePrefix, "filePrefix", "", "file prefix")
	flag.StringVar(&fileSuffix, "fileSuffix", ".txt", "file suffix")
	flag.IntVar(&bathes, "bathes", 0, "count all files for batch from 0 to this value: {filePrefix}{batch}{fileSuffix}")
	flag.StringVar(&resultFilename, "result", "", "path to result file")
	flag.BoolVar(&verbose, "verbose", true, "show logs or not")
}

func main() {
	flag.Parse()
	if filePrefix == "" {
		panic("filePrefix not set")
	}
	if resultFilename == "" {
		panic("result not set")
	}
	if algorithm != "nilsimsa" && algorithm != "simhash" {
		panic("wrong algorithm: it should be nilsimsa | simhash")
	}
	if threshold == -1 {
		if algorithm == "nilsimsa" {
			threshold = 0
		} else {
			threshold = 20
		}
	}

	ctx := context.Background()
	ctx, cancel := context.WithCancel(ctx)

	ch := make(chan string)
	go saveResult(ctx, resultFilename, ch)
	ch <- ":START_ID,:END_ID,score:int,:TYPE\n"

	funcs := []func(ctx context.Context) error{}
	for i := 0; i < bathes; i++ {
		filename1 := fmt.Sprintf("%s%d%s", filePrefix, i, fileSuffix)
		for j := i; j < bathes; j++ {
			filename2 := fmt.Sprintf("%s%d%s", filePrefix, j, fileSuffix)
			funcs = append(funcs, func(funCtx context.Context) error {
				if algorithm == "nilsimsa" {
					return nilsimsaBatch(funCtx, filename1, filename2, ch)
				} else {
					return simhashBatch(funCtx, filename1, filename2, ch)
				}
			})
		}
	}

	err := batchFuncs(ctx, workers, funcs)
	cancel()
	if err != nil {
		panic(err)
	}
}

// example: duplicate -algorithm simhash -workers 32 -filePrefix /home/andrew/cyberok/similarity/temp/test/data -bathes 37 -result res.txt
