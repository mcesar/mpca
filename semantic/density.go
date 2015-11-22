package main

import (
	"bufio"
	"flag"
	"math"
	"os"
	"strings"

	"fmt"
)

type G struct {
	Name     string
	V, E     int
	Vertices []string
}

func (g *G) incV() {
	g.V += 1
}

func (g *G) incE() {
	g.E += 1
}

func main() {
	fileName := flag.String("f", "", "file name")
	percentage := flag.Bool("p", false, "percentage")
	flag.Parse()
	if *fileName == "" {
		fmt.Printf("usage: density -f <file-name>\n")
		return
	}
	clusters := map[string]*G{}
	index := map[string]string{}
	if r, err := os.Open(*fileName); err != nil {
		fmt.Println(err)
		return
	} else {
		scanner := bufio.NewScanner(r)
		var lastCluster *G
		for scanner.Scan() {
			s := scanner.Text()
			if strings.HasPrefix(s, "subgraph") {
				lastCluster = &G{Name: s, Vertices: []string{}}
				clusters[s] = lastCluster
			} else if strings.Index(s, "->") > -1 {
				arr := strings.Split(s, "\" -> \"")
				v1 := arr[0][1:]
				v2 := arr[1][:strings.Index(arr[1], "\"")]
				if index[v1] == index[v2] {
					clusters[index[v1]].incE()
				}
			} else if strings.HasPrefix(s, "\"") && strings.Index(s, "label") > -1 {
				v := s[1:strings.Index(s, "\"[")]
				lastCluster.Vertices = append(lastCluster.Vertices, v)
				index[v] = lastCluster.Name
			}
		}
	}
	sum := 0.0
	squaresum := 0.0
	histogram := [4]float64{}
	for _, c := range clusters {
		d := float64(c.E) / float64((len(c.Vertices) * (len(c.Vertices) - 1)))
		sum += d
		squaresum += d * d
		if len(c.Vertices) <= 2 {
			histogram[0] += 1
		} else if len(c.Vertices) <= 4 {
			histogram[1] += 1
		} else if len(c.Vertices) <= 6 {
			histogram[2] += 1
		} else if len(c.Vertices) > 6 {
			histogram[3] += 1
		}
	}
	mean := sum / float64(len(clusters))
	stddev := math.Sqrt(squaresum/float64(len(clusters)) - mean*mean)
	if *percentage {
		for i := 0; i < 4; i++ {
			histogram[i] = 100 * float64(histogram[i]) / float64(len(clusters))
		}
	}
	fmt.Printf("%.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %d\n",
		mean, stddev, histogram[0], histogram[1], histogram[2], histogram[3], len(clusters))
}
