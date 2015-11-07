package util

import (
	"encoding/xml"
	"os"
	"strings"
)

type SD map[string]*classDependencies

type classDependencies struct {
	Name         string
	Entities     []string
	Superclasses []string
	Dependencies map[string]string
}

type dependencies struct {
	Package []struct {
		Name      string `xml:"name"`
		Confirmed string `xml:"confirmed,attr"`
		Class     []struct {
			Name      string `xml:"name"`
			Confirmed string `xml:"confirmed,attr"`
			Inbound   []port `xml:"inbound"`
			Outbound  []port `xml:"outbound"`
			Feature   []struct {
				Type      string `xml:"type,attr"`
				Confirmed string `xml:"confirmed,attr"`
				Inbound   []port `xml:"inbound"`
				Outbound  []port `xml:"outbound"`
			} `xml:"feature"`
		} `xml:"class"`
	} `xml:"package"`
}

type port struct {
	Type      string `xml:"type,attr"`
	Confirmed string `xml:"confirmed,attr"`
	Value     string `xml:",chardata"`
}

func ParseSD(filename string) (SD, error) {
	var deps dependencies
	if r, err := os.Open(filename); err != nil {
		return nil, err
	} else {
		if err := xml.NewDecoder(r).Decode(&deps); err != nil {
			return nil, err
		}
	}
	sd := SD{}
	packages := map[string]string{}
	for _, p := range deps.Package {
		if p.Confirmed == "yes" {
			packages[p.Name] = p.Name
		}
	}
	for _, p := range deps.Package {
		if p.Confirmed != "yes" {
			continue
		}
		for _, c := range p.Class {
			if c.Confirmed != "yes" {
				continue
			}
			sd[c.Name] = &classDependencies{
				Entities:     []string{},
				Superclasses: []string{},
				Dependencies: map[string]string{}}
			for _, o := range c.Outbound {
				if o.Confirmed == "yes" {
					sd[c.Name].Superclasses = append(sd[c.Name].Superclasses, o.Value)
				}
			}
			for _, f := range c.Feature {
				if f.Confirmed != "yes" {
					continue
				}
				for _, o := range f.Outbound {
					if o.Type != "feature" {
						continue
					}
					cn := className(o.Value)
					found := false
					for _, pp := range packages {
						if strings.HasPrefix(cn, pp) {
							found = true
							break
						}
					}
					if c.Name != cn && found {
						sd[c.Name].Dependencies[cn] = cn
					}
				}
			}
		}
	}
	return sd, nil
}

func className(s string) string {
	if strings.Index(s, "(") < 0 || strings.Index(s[:strings.Index(s, "(")], ".") < 0 {
		return s
	}
	s = s[:strings.Index(s, "(")]
	return s[:strings.LastIndex(s, ".")]
}
