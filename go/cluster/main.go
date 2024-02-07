package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
)

func findClusters(edgesFilename string, skipScore *int, skipScoreMore bool) ([][]string, error) {
	file, err := os.Open(edgesFilename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	clusterNum := 0
	indexToCluster := make(map[string]int)
	clusterToIndices := make(map[int][]string)

	scanner := bufio.NewScanner(file)
	scanner.Scan() // header
	for scanner.Scan() {
		parts := strings.Split(scanner.Text(), ",")
		if skipScore != nil {
			score, err := strconv.Atoi(parts[2])
			if err != nil {
				return nil, err
			}
			if (skipScoreMore && *skipScore > score) || (!skipScoreMore && *skipScore < score) {
				continue
			}
		}
		indexFrom := parts[0]
		indexTo := parts[1]

		clusterFrom, clusterFromExist := indexToCluster[indexFrom]
		clusterTo, clusterToExist := indexToCluster[indexTo]

		if !clusterFromExist {
			if !clusterToExist {
				clusterToIndices[clusterNum] = []string{indexFrom, indexTo}
				indexToCluster[indexFrom] = clusterNum
				indexToCluster[indexTo] = clusterNum
				clusterNum += 1
			} else {
				clusterToIndices[clusterTo] = append(clusterToIndices[clusterTo], indexFrom)
				indexToCluster[indexFrom] = clusterTo
			}
		} else {
			if !clusterToExist {
				clusterToIndices[clusterFrom] = append(clusterToIndices[clusterFrom], indexTo)
				indexToCluster[indexTo] = clusterFrom
			} else {
				if clusterFrom == clusterTo {
					continue
				}
				if len(clusterToIndices[clusterFrom]) > len(clusterToIndices[clusterTo]) {
					clusterToOld := clusterTo
					clusterTo = clusterFrom
					clusterFrom = clusterToOld
				}
				indices := clusterToIndices[clusterFrom]
				delete(clusterToIndices, clusterFrom)
				clusterToIndices[clusterTo] = append(clusterToIndices[clusterTo], indices...)
				for _, index := range indices {
					indexToCluster[index] = clusterTo
				}
			}
		}
	}

	if err := scanner.Err(); err != nil {
		return nil, err
	}

	clusters := make([][]string, 0, len(clusterToIndices))
	for _, cluster := range clusterToIndices {
		clusters = append(clusters, cluster)
	}

	sort.SliceStable(clusters, func(i, j int) bool {
		return len(clusters[i]) > len(clusters[j])
	})

	return clusters, nil
}

func showCluster(cluster []string) string {
	res := make([]string, 0, len(cluster))
	for _, index := range cluster {
		res = append(res, index)
	}

	return strings.Join(res, " ")
}

func findAndSaveClusters(edgesFilename, resultFilename string, skipScore *int, skipScoreMore bool) error {
	clusters, err := findClusters(edgesFilename, skipScore, skipScoreMore)
	if err != nil {
		return err
	}

	file, err := os.Create(resultFilename)
	if err != nil {
		return err
	}
	defer file.Close()

	w := bufio.NewWriter(file)
	for _, cluster := range clusters {
		fmt.Fprintln(w, showCluster(cluster))
	}
	return w.Flush()
}

var (
	filenameFrom  string
	filenameTo    string
	skipScore     int
	skipScoreMore bool
)

func init() {
	flag.StringVar(&filenameFrom, "filenameFrom", "", "path to edges csv")
	flag.StringVar(&filenameTo, "filenameTo", "", "path to result - clusters txt")
	flag.IntVar(&skipScore, "skipScore", -1, "skip score for alg")
	flag.BoolVar(&skipScoreMore, "skipScoreMore", true, "filter skipScore <= `score`, otherwise skipScore >= `score`; simhash, tlsh - false, mrsh, nilsimsa, ssdeep - true")
}

func main() {
	flag.Parse()
	if filenameFrom == "" {
		panic("filenameFrom not set")
	}
	if filenameTo == "" {
		panic("filenameTo not set")
	}
	var skipScoreValue *int = nil
	if skipScore != -1 {
		skipScoreValue = &skipScore
	}

	if err := findAndSaveClusters(filenameFrom, filenameTo, skipScoreValue, skipScoreMore); err != nil {
		fmt.Println(err.Error())
	}
}

// example: cluster -filenameFrom /home/andrew/cyberok/duplicate/db/import/mrsh_edges.csv -filenameTo /home/andrew/cyberok/duplicate/rooster/clusters/mrsh.txt -skipScore 30 --skipScoreMore=true
