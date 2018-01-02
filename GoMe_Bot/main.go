package main

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type GroupMessagesResponseWrapper struct {
	Response GroupMessagesResponse  `json:"response"`
	Meta     map[string]interface{} `json:"meta"`
}

type GroupMessagesResponse struct {
	Count    int              `json:"count"`
	Messages []GroupMeMessage `json:"messages"`
}

type GroupMeMessage struct {
	//Attachments []GroupMeMessageAttachment `json:"attachments"`
	//AvatarURL   string                     `json:"avatar_url"`
	//CreatedAt   int                        `json:"created_at"`
	FavoritedBy []string `json:"favorited_by"`
	//GroupID     string                     `json:"group_id"`
	//ID         string `json:"id"`
	Name       string `json:"name"`
	SenderID   string `json:"sender_id"`
	SenderType string `json:"sender_type"`
	//SourceGUID  string                     `json:"source_guid"`
	//System      bool                       `json:"system"`
	Text   string `json:"text"`
	UserID string `json:"user_id"`
}

type GroupMeMessageAttachment struct {
	Type    string   `json:"type"`
	UserIDs []string `json:"user_ids"`
	Loci    [][]int  `json:"loci"`
	URL     string   `json:"url"`
}

type GroupInfoResponseWrapper struct {
	Response GroupInfoResponse      `json:"response"`
	Meta     map[string]interface{} `json:"meta"`
}

type GroupInfoResponse struct {
	//GroupID     string          `json:"group_id"`
	Name        string `json:"name"`
	Description string `json:"description"`
	//ImageURL    string          `json:"image_url"`
	Members []GroupMeMember `json:"members"`
}

type GroupMeMember struct {
	UserID string `json:"user_id"`
	ID     string `json:"id"`
	Name   string `json:"nickname"`
	//AvatarURL string `json:"image_url"`
}

func parseMessages() {
	groupID := "9672911"
	token := "03Y3Q6VCHem5jGABvaPnZHEBN7ipxPHdTiEKbxL2"
	url := "https://api.groupme.com/v3/groups/" + groupID + "/messages?token=" + token
	resp, _ := http.Get(url)

	defer resp.Body.Close()
	decoder := json.NewDecoder(resp.Body)

	var data GroupMessagesResponseWrapper
	decoder.Decode(&data)

	for i := 0; i < len(data.Response.Messages); i++ {
		fmt.Println(data.Response.Messages[i])
	}
}

func main() {
	/*
		groupID := "9672911"
		token := "03Y3Q6VCHem5jGABvaPnZHEBN7ipxPHdTiEKbxL2"
		//url := "https://api.groupme.com/v3/groups/" + groupID + "/messages?token=" + token
		url := "https://api.groupme.com/v3/groups/" + groupID + "?token=" + token
		resp, _ := http.Get(url)

		defer resp.Body.Close()

		decoder := json.NewDecoder(resp.Body)

		//var data GroupMessagesResponseWrapper
		var data GroupInfoResponseWrapper
		decoder.Decode(&data)

		//fmt.Println(data.Response.Messages)
		fmt.Println(data.Response)
	*/
	parseMessages()
}
