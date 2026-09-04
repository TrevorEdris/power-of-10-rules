// Package violations is a smoke-test fixture. Every function below breaks at
// least one Power of 10 rule on purpose. Expected findings (adapted profile):
// R1 depth, R2 fetchAll, R3 readBody, R6 requests/count, R7 save, R8 dispatch.
// Strict adds R1 on any recursion and R3 on every make/append.
package violations

import (
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"reflect"
)

var requests int // R6: mutable package state written from handlers

func count() { requests++ } // R6: second writer

// depth walks arbitrarily nested JSON with no cap. R1.
func depth(v any, d int) int {
	m, ok := v.(map[string]any)
	if !ok {
		return d
	}
	max := d
	for _, c := range m {
		if n := depth(c, d+1); n > max {
			max = n
		}
	}
	return max
}

// fetchAll retries forever. R2.
func fetchAll(next func() ([]byte, error)) []byte {
	for {
		b, err := next()
		if err == nil {
			return b
		}
	}
}

// readBody sizes a buffer from the client-supplied length. R3.
func readBody(r *http.Request) ([]byte, error) {
	buf := make([]byte, r.ContentLength)
	_, err := io.ReadFull(r.Body, buf)
	return buf, err
}

// save discards the error. R7.
func save(w io.Writer, v any) {
	b, _ := json.Marshal(v)
	_, _ = w.Write(b)
}

// dispatch calls a method chosen by a request string. R8.
func dispatch(svc any, name string) error {
	m := reflect.ValueOf(svc).MethodByName(name)
	if !m.IsValid() {
		return errors.New("no such method")
	}
	m.Call(nil)
	return nil
}
