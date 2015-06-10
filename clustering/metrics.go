package main

import (
	"encoding/xml"
	"flag"
	"io/ioutil"
	"os"
	"strings"

	"fmt"
)

type LDI struct {
	Elements []struct {
		Name string `xml:"name,attr"`
		Uses []struct {
			Provider string `xml:"provider,attr"`
			Kind     string `xml:"kind,attr"`
		} `xml:"uses"`
	} `xml:"element"`
}

func main() {
	fileName := flag.String("f", "", "file name")
	ignoreString := flag.String("i", "", "ignore kinds")
	metric := flag.String("m", "ai", "metric name")
	flag.Parse()
	ignore := strings.Split(*ignoreString, ",")
	if ldi, err := parseLDI(*fileName); err != nil {
		fmt.Printf("error: %v\n", err)
	} else {
		if *metric == "ai" {
			matrix, _, _ := ldi.dependencyMatrix(ignore)
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
		} else if *metric == "ic" {
			matrix, _, _ /*index*/ := ldi.dependencyMatrix(ignore)
			warshall(matrix)
			// Compute intercomponent cyclicality
			cycle := map[int]byte{}
			for i := range matrix {
				for j := range matrix {
					if matrix[i][j] && matrix[j][i] { // in cycle
						// n1 := index[i]
						// n2 := index[j]
						//if n1[:strings.LastIndex(n1, ".")] != n2[:strings.LastIndex(n2, ".")] {
						cycle[i] = 1
						//}
					}
				}
			}
			fmt.Println(len(cycle), len(matrix))
		}
	}
}

// Compute transitive closure
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

func parseLDI(fileName string) (*LDI, error) {
	var ldi LDI
	if r, err := os.Open(fileName); err != nil {
		return nil, err
	} else {
		if bytes, err := ioutil.ReadAll(r); err != nil {
			return nil, err
		} else {
			if err := xml.Unmarshal(bytes, &ldi); err != nil {
				return nil, err
			}
		}
	}
	return &ldi, nil
}

func (ldi *LDI) dependencyMatrix(ignore []string) ([][]bool, map[string]int, map[int]string) {
	matrix := make([][]bool, len(ldi.Elements))
	arr := make([]bool, len(ldi.Elements)*len(ldi.Elements))
	for i := range matrix {
		matrix[i], arr = arr[:len(ldi.Elements)], arr[len(ldi.Elements):]
	}
	index := map[string]int{}
	reverseIndex := map[int]string{}
	for i, e := range ldi.Elements {
		index[e.Name] = i
		reverseIndex[i] = e.Name
	}
	for _, e := range ldi.Elements {
		for _, u := range e.Uses {
			kind := u.Kind
			if kind == "" {
				kind = "static"
			}
			if !hasElement(kind, ignore) {
				matrix[index[e.Name]][index[u.Provider]] = true
			}
		}
	}
	return matrix, index, reverseIndex
}

func hasElement(e string, s []string) bool {
	for _, each := range s {
		if e == each {
			return true
		}
	}
	return false
}
