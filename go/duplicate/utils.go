package main

import (
	"context"
	"fmt"
	"sync/atomic"

	"golang.org/x/sync/semaphore"
)

func batchFuncs(ctx context.Context, workers int64, fs []func(ctx context.Context) error) error {
	ctx, cancel := context.WithCancel(ctx)
	ch := make(chan error)

	var index int64 = 0
	semCtx := context.TODO()
	sem := semaphore.NewWeighted(workers)
	for _, f := range fs {
		go func(f func(ctx context.Context) error) {
			if err := sem.Acquire(semCtx, 1); err != nil {
				ch <- err
				return
			}
			defer sem.Release(1)
			select {
			case <-ctx.Done():
				ch <- fmt.Errorf("canceled")
			default:
				ch <- f(ctx)
				atomic.AddInt64(&index, 1)
				if verbose {
					fmt.Printf("done %d/%d\n", index, len(fs))
				}
			}
		}(f)
	}

	var firstErr error
	for i := 0; i < len(fs); i++ {
		if err := <-ch; err != nil {
			if firstErr == nil {
				firstErr = err
				cancel()
			}
		}
	}

	close(ch)
	return firstErr
}
