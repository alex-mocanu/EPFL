package main // import "main"

import (
	"encoding/hex"
	"fmt"
	//"io/ioutil"
	"os"
	"strings"

	"go.dedis.ch/cothority/v3"
	"go.dedis.ch/cothority/v3/skipchain"
	"go.dedis.ch/onet/v3"
	"go.dedis.ch/onet/v3/network"
)

const email = "<YOUR EMAIL>"

func main() {
	if len(os.Args) <= 1 {
		fmt.Println("Missing URL (tls://com402.epfl.ch:7002)")
		os.Exit(1)
	}
	// Get the address
	arg := os.Args[1]

	roster := onet.NewRoster([]*network.ServerIdentity{
		&network.ServerIdentity{
			Address: network.Address(arg),
			// necessary to create a roster..
			Public: cothority.Suite.Point(),
		},
	})

	bb := "6a6ea0e9f701862ddd746ad80d331fc4834a5f358443572eadc138a93cfdbd3a"

	id, err := hex.DecodeString(strings.Trim(bb, "\n"))
	if err != nil {
		fmt.Printf("%v\n", err)
		os.Exit(1)
	}
	//This is the genesis id
	sid := skipchain.SkipBlockID(id)

	//Creating a new client for the skipchain
	cl := skipchain.NewClient()
	
	// Get the latest block for the hash -- Add your code here
	fmt.Println("Get latest block: Add code")

	// Mine a correct hash with 3 leading 0 bytes -- Add your code here
	fmt.Println("Mine a correct hash with 3 leading 0 bytes: Add code")
	
	//Store the new block -- Add your code here
	fmt.Println("Storing the new block: Add code")

}
