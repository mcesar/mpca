package main

import (
	"fmt"
	"os"

	"../../../util"
)

func main() {
	sd, err := util.ParseSD(os.Args[1])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
	}
	ldi := &util.LDI{}
	for cn, c := range sd {
		m := map[string]string{}
		for _, d := range c.Dependencies {
			m[d] = "static"
		}
		ldi.Append(cn, m)
	}
	err = ldi.Render(os.Stdout)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
	}
}
