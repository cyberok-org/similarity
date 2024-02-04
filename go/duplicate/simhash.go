package main

type Simhash interface {
	Compare(digest1, digest2 uint64) int
}

type SimhashImpl struct {
	features int
}

var _ Simhash = (*SimhashImpl)(nil)

func NewSimhash() Simhash {
	return &SimhashImpl{features: 64}
}

func (si *SimhashImpl) Compare(digest1, digest2 uint64) int {
	x := (digest1 ^ digest2) & ((1 << si.features) - 1)
	ans := 0
	for x != 0 {
		ans += 1
		x &= x - 1
	}
	return ans
}
