package main

import (
	"encoding/json"
	log "github.com/sirupsen/logrus"
	"net/http"
	"net/url"
	"strconv"
)

func handleSticker(w http.ResponseWriter, updateMessage *Message, botLog *log.Entry) {
	botLog.WithFields(
		log.Fields{
			"command": "sticker",
			"emoji":   updateMessage.Sticker.Emoji,
			"file_id": updateMessage.Sticker.FileID,
		}).Debug("Sticker received")
	answerMessage(w, updateMessage.Chat.ID, "sticker", "Я еще не знаю, что с ним делать. Посмотри в логах")
}

func sendSticker(chatID int64, sticker_name string) {
	sticker, ok := stickerSet[sticker_name]
	if !ok {
		log.WithFields(log.Fields{"chat": chatID, "sticker": sticker_name}).Error("Sticker not found")
		return
	}
	_, err := http.PostForm(
		"https://api.telegram.org/bot"+config.Token+"/sendSticker",
		url.Values{
			"chat_id": {strconv.FormatInt(chatID, 10)},
			"sticker": {sticker.FileID},
		})
	if err != nil {
		log.WithFields(log.Fields{"chat": chatID, "sticker": sticker_name}).Error(err.Error())
	}
}

func answerSticker(w http.ResponseWriter, chatID int64, command, sticker_name string) {
	sticker, ok := stickerSet[sticker_name]
	if !ok {
		log.WithFields(log.Fields{"chat": chatID, "command": command, "sticker": sticker_name}).Error("Sticker not found")
		return
	}
	msg := Response{Chatid: chatID, Sticker: &sticker.FileID, Method: "sendSticker"}
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)
	log.WithFields(log.Fields{"chat": chatID, "command": command}).Debug(sticker_name)
	json.NewEncoder(w).Encode(msg)
}

var stickerSet = map[string]Sticker{
	"Ждун Error":      Sticker{Emoji: "😥", FileID: "CAADAgADXAIAAkcVaAmc8uhlUE4ieAI"},
	"meh":             Sticker{Emoji: "😒", FileID: "CAADAgADXAADgGsjBmPStIDI-4GcAg"},
	"SimonCat":        Sticker{Emoji: "😊", FileID: "CAADAgADTxUAAkKvaQABYO6WZm1tea0C"},
	"Хуяк в Продакшн": Sticker{Emoji: "😎", FileID: "CAADAgADOwAD3W4LAAH3w0JtBvzbBAI"},
	"Нормально Делай": Sticker{Emoji: "🤓", FileID: "CAADAgADOQAD3W4LAAGgNFabvTJ0YQI"},
	"А вот и Я":       Sticker{Emoji: "😉", FileID: "CAADAgADBCAAAp7OCwABGh2pHw4IibgC"},
	"Я Сделяль":       Sticker{Emoji: "☹", FileID: "CAADAgADVQIAAoBrIwZYTAonqLtuZgI"},
}
