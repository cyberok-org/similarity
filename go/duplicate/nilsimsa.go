package main

import "strconv"

type Nilsimsa interface {
	ConvertHexToInts(hexdigest string) ([]int, error)

	Compare(digest1, digest2 []int) int
}

type NilsimsaImpl struct{}

var _ Nilsimsa = (*NilsimsaImpl)(nil)

var (
	popc = []int{0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 4, 5, 5, 6, 5, 6, 6, 7, 5, 6, 6, 7, 6, 7, 7, 8}
)

func NewNilsimsa() Nilsimsa {
	return &NilsimsaImpl{}
}

func (ni *NilsimsaImpl) ConvertHexToInts(hexdigest string) ([]int, error) {
	ints := make([]int, 0)
	for i := 0; i < 64; i += 2 {
		i, err := strconv.ParseInt(hexdigest[i:i+2], 16, 64)
		if err != nil {
			return nil, err
		}
		ints = append(ints, int(i))
	}
	return ints, nil
}

func (ni *NilsimsaImpl) Compare(digest1, digest2 []int) int {
	bit_diff := 0
	for i, num := range digest1 {
		num2 := digest2[i]
		bit_diff += popc[num^num2]
	}
	return 128 - bit_diff
}
