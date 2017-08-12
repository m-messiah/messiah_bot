package main

// Main Bot class
type Bot struct {
}

type Config struct {
	Port     int64
	LogLevel string
	Name     string
	Admins   []int64
	Token    string
}

// Response to Telegram
type Response struct {
	Chatid int64  `json:"chat_id"`
	Text   string `json:"text"`
	Method string `json:"method"`
}

// Chat Telegram structure
type Chat struct {
	ID int64 `json:"id"`
}

// Message Telegram structure
type Message struct {
	Chat *Chat  `json:"chat"`
	Text string `json:"text"`
}

// Update - outer Telegram structure
type Update struct {
	Message *Message `json:"message"`
}
