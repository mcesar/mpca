package main

import (
	"flag"
	"os"
	"strings"

	"fmt"

	"../util"
)

func main() {
	fileName := flag.String("f", "", "file name")
	ignoreString := flag.String("i", "", "ignore kinds")
	metric := flag.String("m", "ai", "metric name")
	flag.Parse()
	ignore := strings.Split(*ignoreString, ",")
	if *metric == "packages" {
		packages := map[string]int{}
		if err := collectPackages(*fileName, packages); err != nil {
			fmt.Printf("error: %v\n", err)
		} else {
			for k, _ := range packages {
				fmt.Printf("%v\n", k)
			}
		}
		return
	}
	if l, err := ldi.Parse(*fileName); err != nil {
		fmt.Printf("error: %v\n", err)
	} else {
		if *metric == "ai" {
			matrix, _, _ := l.DependencyMatrix(ignore)
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
			matrix, _, _ /*index*/ := l.DependencyMatrix(ignore)
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

func collectPackages(fileName string, packages map[string]int) error {
	if f, err := os.Open(fileName); err != nil {
		return err
	} else {
		defer f.Close()
		if fi, err := f.Readdir(0); err != nil {
			fmt.Printf("error: %v\n", err)
		} else {
			for _, entry := range fi {
				if strings.Contains(entry.Name(), ".f") {
					packages[fileName] = 0
				}
				if entry.IsDir() {
					fullEntryName := fileName + string(os.PathSeparator) + entry.Name()
					if err = collectPackages(fullEntryName, packages); err != nil {
						return err
					}
				}
			}
		}
		return nil
	}
}
