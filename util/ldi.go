package ldi

import (
	"encoding/xml"
	"io/ioutil"
	"os"
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

func Parse(fileName string) (*LDI, error) {
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
	for _, e := range ldi.Elements {
		for _, u := range e.Uses {
			if u.Kind == "" {
				u.Kind = "static"
			}
		}
	}
	return &ldi, nil
}

func (ldi *LDI) DependencyMatrix(ignore []string) ([][]bool, map[string]int, map[int]string) {
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
			if !HasElement(u.Kind, ignore) {
				matrix[index[e.Name]][index[u.Provider]] = true
			}
		}
	}
	return matrix, index, reverseIndex
}

func HasElement(e string, s []string) bool {
	for _, each := range s {
		if e == each {
			return true
		}
	}
	return false
}
