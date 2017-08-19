package main

import (
	"bytes"
	"encoding/binary"
	"errors"
	"net"
)

// This function gets the address associated with an interface
func GetIpFromInterface(iface string) (*net.UDPAddr, error) {
	ief, err := net.InterfaceByName(iface)
	if err != nil {
		return nil, err
	}

	addrs, err := ief.Addrs()
	if err != nil {
		return nil, err
	} else if len(addrs) <= 0 {
		return nil, errors.New("No address associated with interface " + iface)
	}

	// Validate that one of the addr's is a valid network IP address
	for _, addr := range addrs {
		switch ip := addr.(type) {
		case *net.IPNet:
			// Verify that the DefaultMask for the address we want to use exists
			if ip.IP.DefaultMask() != nil {
				return &net.UDPAddr{
					IP: ip.IP,
				}, nil
			}
		}
	}
	return nil, errors.New("Unable to find valid IP addr for interface " + iface)
}

func SendMagicPacket(mac string) error {
	var packet MagicPacket
	var macAddr MACAddress
	packet.header = [6]byte{0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}
	hwAddr, err := net.ParseMAC(mac)
	if err != nil {
		return err
	}

	// Copy bytes from the returned HardwareAddr -> a fixed size
	// MACAddress
	for idx := range macAddr {
		macAddr[idx] = hwAddr[idx]
	}

	for idx := range packet.payload {
		packet.payload[idx] = macAddr
	}
	// Fill our byte buffer with the bytes in our MagicPacket
	var buf bytes.Buffer
	binary.Write(&buf, binary.BigEndian, packet)
	// Get a UDPAddr to send the broadcast to
	udpAddr, err := net.ResolveUDPAddr("udp", "255.255.255.255:9")
	if err != nil {
		return err
	}
	var localAddr *net.UDPAddr
	// Open a UDP connection, and defer it's cleanup
	connection, err := net.DialUDP("udp", localAddr, udpAddr)
	if err != nil {
		return errors.New("Unable to dial UDP address.")
	}
	defer connection.Close()

	// Write the bytes of the MagicPacket to the connection
	_, err = connection.Write(buf.Bytes())
	if err != nil {
		return err
	}
	return nil
}
