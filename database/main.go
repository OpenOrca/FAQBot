package main

import (
	"context"
	"os"

	"log"

	"github.com/eugenepentland/VectorPB/functions"
	"github.com/nlpodyssey/cybertron/pkg/tasks"
	"github.com/pocketbase/pocketbase"
	"github.com/pocketbase/pocketbase/core"
)

// 32 in bytes is a space
// 10 13 is a new line
func main() {
	runApp()
}

func runApp() {
	//Initalizes the pocketbase app
	app := pocketbase.New()
	ctx := context.Background()
	//Initalizes the embedding model
	modelsDir := "./models"
	//Loads the model
	m, err := tasks.LoadModelForTextEncoding(&tasks.Config{ModelsDir: modelsDir, ModelName: "sentence-transformers/all-MiniLM-L6-v2"})
	if err != nil {
		log.Fatal(err)
	}

	//Initializes the database collections
	app.OnBeforeServe().Add(functions.InitializeEmbeddingDB)

	app.OnRecordBeforeCreateRequest().Add(func (e *core.RecordCreateEvent) error {
		functions.AddVectorOnCreate(e, m, ctx)
		return nil
	})

	//Adds the custom fuctions to the database
	app.OnRecordsListRequest().Add(func(e *core.RecordsListEvent) error {
		functions.VectorSearch(e, m, ctx)
		return nil
	})

	//Sets the default args for the serve command
	os.Args = append(os.Args, "--http=127.0.0.1:8091")
	os.Args = append(os.Args, "serve")
	if err := app.Start(); err != nil {
		log.Fatal(err)
	}
}
