package functions

import (
	"context"
	"fmt"
	"sort"

	"github.com/nlpodyssey/cybertron/pkg/models/bert"
	"github.com/nlpodyssey/cybertron/pkg/tasks/textencoding"
	"github.com/pocketbase/pocketbase/core"
	"github.com/pocketbase/pocketbase/models"
)

func InitializeEmbeddingDB(e *core.ServeEvent) error {
	// UpsertFileTable(e.App)
	// UpsertEmbeddingTable(e.App)
	return nil
}

type Metadata struct {
	Loc Loc `json:"loc"`
}

type Loc struct {
	PageNumber int `json:"pageNumber"`
	PageIndex  int `json:"pageIndex"`
}

type EmbeddingPayload struct {
	Text      string    `json:"text"`
	Embedding []float64 `json:"embedding"`
}

func GetSimilarityScore(Embedding EmbeddingPayload, EmbeddingList []EmbeddingPayload) float64 {
	var score float64 = 0
	for i := 0; i < len(EmbeddingList); i++ {
		similarity, err := Cosine(Embedding.Embedding, EmbeddingList[i].Embedding)
		if err != nil {
			fmt.Println(err)
		}
		score += similarity
	}
	return score / float64(len(EmbeddingList))
}

func AddVectorOnCreate(e *core.RecordCreateEvent, m textencoding.Interface, ctx context.Context) error {
	if e.Record.Collection().Name != "questions" {
		return nil
	}
	text := e.Record.GetString("text")
	if text == "" {
		return nil
	}
	poolingStrat := int(bert.MeanPooling)
	result, err := m.Encode(ctx, text, poolingStrat)
	if err != nil {
		return err
	}
	queryVector := result.Vector.Data().F64()
	e.Record.Set("embedding", queryVector)
	return nil
}

func VectorSearch(e *core.RecordsListEvent, m textencoding.Interface, ctx context.Context) error {
	searchQuery := e.HttpContext.QueryParam("search")
	if searchQuery == "" {
		return nil
	}
	poolingStrat := int(bert.MeanPooling)
	result, err := m.Encode(ctx, searchQuery, poolingStrat)
	if err != nil {
		return err
	}
	queryVector := result.Vector.Data().F64()

	var similarRecords []*models.Record

	for i, v := range e.Records {
		var recordVector []float64
		err := v.UnmarshalJSONField("embedding", &recordVector)
		if err != nil {
			fmt.Println(err)
			continue
		}

		similarity, err := Cosine(queryVector, recordVector)
		if err != nil {
			fmt.Println(err)
			continue
		}

		e.Records[i].Set("similarity", similarity)
		similarRecords = append(similarRecords, v)
	}
	// Sort results by similarity in descending order
	sort.Slice(similarRecords, func(i, j int) bool {
		return similarRecords[i].GetFloat("similarity") >= similarRecords[j].GetFloat("similarity")
	})
	if len(similarRecords) >= 1 {
		e.Result.Items = similarRecords[:1]
	} else {
		e.Result.Items = similarRecords
	}
	return nil
}
