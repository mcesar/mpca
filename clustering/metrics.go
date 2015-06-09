package main

import (
	"encoding/xml"
	"flag"
	"io/ioutil"
	"os"
	"strings"

	"fmt"
)

func main() {
	var ldi struct {
		Elements []struct {
			Name string `xml:"name,attr"`
			Uses []struct {
				Provider string `xml:"provider,attr"`
				Kind     string `xml:"kind,attr"`
			} `xml:"uses"`
		} `xml:"element"`
	}
	fileName := flag.String("f", "", "file name")
	ignoreString := flag.String("i", "", "ignore kinds")
	flag.Parse()
	ignore := strings.Split(*ignoreString, ",")
	// Parse XML
	if r, err := os.Open(*fileName); err != nil {
		fmt.Printf("error: %v\n", err)
		return
	} else {
		if bytes, err := ioutil.ReadAll(r); err != nil {
			fmt.Printf("error: %v\n", err)
			return
		} else {
			if err := xml.Unmarshal(bytes, &ldi); err != nil {
				fmt.Printf("error: %v\n", err)
				return
			}
		}
	}
	// Build Matrix
	matrix := make([][]bool, len(ldi.Elements))
	arr := make([]bool, len(ldi.Elements)*len(ldi.Elements))
	for i := range matrix {
		matrix[i], arr = arr[:len(ldi.Elements)], arr[len(ldi.Elements):]
	}
	index := map[string]int{}
	for i, e := range ldi.Elements {
		index[e.Name] = i
	}
	for _, e := range ldi.Elements {
		for _, u := range e.Uses {
			kind := u.Kind
			if kind == "" {
				kind = "static"
			}
			mustIgnore := false
			for _, ig := range ignore {
				if kind == ig {
					mustIgnore = true
					break
				}
			}
			if !mustIgnore {
				matrix[index[e.Name]][index[u.Provider]] = true
			}
		}
	}
	// Compute transitive closure
	warshall(matrix)
	// Compute average impact
	count := 0
	for i := range matrix {
		for j := range matrix {
			if matrix[i][j] {
				count += 1
			}
		}
	}
	fmt.Printf("\n%v %v %v\n", count/len(matrix), count, len(matrix))
}

func warshall(a [][]bool) {
	for k := range a {
		fmt.Print(".")
		for i := range a {
			for j := range a {
				a[i][j] = a[i][j] || (a[i][k] && a[k][j])
			}
		}
	}
}
