package main

import (
	"github.com/BurntSushi/toml"
	log "github.com/sirupsen/logrus"
	"net/http"
	"os"
	"strconv"
)

var config Config

func main() {
	log.SetOutput(os.Stdout)

	if len(os.Args) < 2 {
		log.Fatal("No config path passed")
		os.Exit(2)
	}
	config_path := os.Args[1]
	_, err := toml.DecodeFile(config_path, &config)
	if err != nil {
		log.WithFields(log.Fields{"config": config_path}).Fatal(err.Error())
		os.Exit(2)
	}
	port := strconv.FormatInt(config.Port, 10)
	loglevel, err := log.ParseLevel(config.LogLevel)
	if err != nil {
		log.WithFields(log.Fields{"config": config_path}).Fatal(err.Error())
		os.Exit(2)
	}
	log.SetLevel(loglevel)
	http.HandleFunc("/", BotHandle)
	log.WithFields(log.Fields{"port": port}).Info("Start bot server")
	http.ListenAndServe(":"+port, nil)
}
