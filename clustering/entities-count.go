package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintf(os.Stderr, "usage: entities-count <mdg>\n")
		return
	}
	f, err := os.Open(os.Args[1])
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		return
	}
	s := bufio.NewScanner(f)
	m := map[string]int{}
	for s.Scan() {
		arr := strings.Split(s.Text(), " ")
		m[arr[0]]++
		m[arr[1]]++
	}
	if s.Err() != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", s.Err())
		return
	}
	fmt.Println(len(m))
}
