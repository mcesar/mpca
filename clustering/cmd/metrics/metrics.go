package main

import (
	"flag"
	"log"
	"math"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"fmt"

	"../../../util"
)

func main() {
	fileName := flag.String("f", "", "file name")
	ignoreString := flag.String("i", "", "ignore kinds")
	metric := flag.String("m", "ai", "metric name")
	noTransitiveClosure := flag.Bool("t", false, "no transitive closure")
	flag.Parse()
	ignore := strings.Split(*ignoreString, ",")
	if *fileName == "" {
		flag.Usage()
		return
	}
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
	if *metric == "instability" {
		file, err := os.Open(*fileName)
		if err != nil {
			log.Fatal("An error occurred while opening file ", err)
		}
		defer file.Close()
		fi, err := file.Stat()
		if err != nil {
			log.Fatal("An error occurred ", err)
		}
		var names []string
		if fi.IsDir() {
			names, err = file.Readdirnames(0)
		} else {
			names = []string{*fileName}
		}
		file.Close()
		s := 0.0
		r := 0.0
		n := 0
		for _, fn := range names {
			if !strings.HasSuffix(fn, ".xml") {
				continue
			}
			if i, err := util.ParseInstability(filepath.Join(*fileName, fn)); err != nil {
				fmt.Printf("error: %v\n", err)
			} else {
				for _, c := range i.Class {
					s += c.Probability
					r += c.REM
				}
				n += len(i.Class)
			}
		}
		fmt.Println(s/float64(n), r/float64(n))
		return
	}
	l, err := util.ParseLDI(*fileName)
	if err != nil {
		fmt.Printf("error: %v\n", err)
	}
	if *metric == "ai" {
		matrix, _, _ := l.DependencyMatrix(ignore)
		if !*noTransitiveClosure {
			warshall(matrix)
		}
		// Compute average impact
		count := 0
		for i := range matrix {
			for j := range matrix {
				if matrix[i][j] {
					count += 1
				}
			}
		}
		fmt.Printf("\nAI=%v PC=%v D=%v N=%v\n",
			float64(count)/float64(len(matrix)),
			float64(count)/float64(len(matrix)*len(matrix)),
			count, len(matrix))
	} else if *metric == "ic" {
		matrix, _, _ /*index*/ := l.DependencyMatrix(ignore)
		if !*noTransitiveClosure {
			warshall(matrix)
		}
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
	} else if *metric == "coincides" {
		static, _, _ := l.DependencyMatrix([]string{"evolutionary"})
		evolutionary, _, _ := l.DependencyMatrix([]string{"static"})
		if !*noTransitiveClosure {
			warshall(static)
			warshall(evolutionary)
		}
		staticCount := 0
		evolutionaryCount := 0
		staticAndEvolutionaryCount := 0
		for i := range static {
			for j := range static {
				if static[i][j] {
					staticCount++
					if evolutionary[i][j] {
						staticAndEvolutionaryCount++
					}
				}
				if evolutionary[i][j] {
					evolutionaryCount++
				}
			}
		}
		count := staticCount + evolutionaryCount - staticAndEvolutionaryCount
		fmt.Println(count, staticCount,
			float64(staticAndEvolutionaryCount)/float64(count),
			float64(staticAndEvolutionaryCount)/float64(staticCount))
	} else if *metric == "stats" {
		m := map[string]int{}
		sum := 0
		for _, e := range l.Elements {
			i := strings.LastIndex(e.Name, ".")
			m[e.Name[:i]]++
			sum++
		}
		dist := make([]int, len(m))
		squaresum := 0.0
		i := 0
		for _, v := range m {
			dist[i] = v
			squaresum += float64(v * v)
			i++
		}
		sort.Ints(dist)
		mean := float64(sum) / float64(len(m))
		stddev := math.Sqrt(squaresum/float64(len(m)) - mean*mean)
		fmt.Printf("%.2f & %.2f & %d & %d & %d & %d & %d\n",
			mean, stddev, dist[0], dist[len(dist)-1], dist[len(dist)/2], sum, len(m))
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
			return err
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
