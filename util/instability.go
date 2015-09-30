package util

import (
	"encoding/xml"
	"io/ioutil"
	"os"
	"regexp"
	"strconv"
)

type ClassInstability struct {
	Name  string `xml:"name"`
	Class []struct {
		Name        string  `xml:"name"`
		Probability float64 `xml:"tot_prob"`
		REM         float64
		Axis        []struct {
			Description string `xml:"description"`
			To          string `xml:"to"`
		} `xml:"axis"`
	} `xml:"class"`
}

func ParseInstability(fileName string) (*ClassInstability, error) {
	var ci ClassInstability
	if r, err := os.Open(fileName); err != nil {
		return nil, err
	} else {
		if bytes, err := ioutil.ReadAll(r); err != nil {
			return nil, err
		} else {
			if err := xml.Unmarshal(bytes, &ci); err != nil {
				return nil, err
			}
		}
	}
	r, err := regexp.Compile("\\(propagation factor: (\\d+\\.\\d+)\\)")
	if err != nil {
		return nil, err
	}
	for i, _ := range ci.Class {
		rem := 1.0
		for j, _ := range ci.Class[i].Axis {
			f, err := strconv.ParseFloat(r.FindStringSubmatch(ci.Class[i].Axis[j].To)[1], 64)
			if err != nil {
				return nil, err
			}
			rem *= (1.0 - f)
		}
		ci.Class[i].REM = 1 - rem
	}
	return &ci, nil
}
