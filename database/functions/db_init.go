package functions

import (
	"fmt"

	"github.com/pocketbase/pocketbase/core"
	"github.com/pocketbase/pocketbase/forms"
	"github.com/pocketbase/pocketbase/models"
	"github.com/pocketbase/pocketbase/models/schema"
	"github.com/pocketbase/pocketbase/tools/types"
)

func UpsertEmbeddingTable(app core.App) error {
	collectionName := "embeddings"
	_, err := app.Dao().FindCollectionByNameOrId(collectionName)
	if err == nil {
		return nil
	}
	collection := &models.Collection{}
	form := forms.NewCollectionUpsert(app, collection)
	form.Name = collectionName
	form.Type = models.CollectionTypeBase
	form.ListRule = nil
	form.ViewRule = nil
	form.CreateRule = nil
	form.UpdateRule = nil
	form.DeleteRule = nil
	form.Schema.AddField(&schema.SchemaField{
		Name:     "text",
		Type:     schema.FieldTypeText,
		Required: true,
	})
	form.Schema.AddField(&schema.SchemaField{
		Name:     "model",
		Type:     schema.FieldTypeText,
		Required: true,
	})
	form.Schema.AddField(&schema.SchemaField{
		Name:     "similarity",
		Type:     schema.FieldTypeNumber,
		Required: false,
	})
	form.Schema.AddField(&schema.SchemaField{
		Name:     "token_count",
		Type:     schema.FieldTypeNumber,
		Required: true,
	})
	form.Schema.AddField(&schema.SchemaField{
		Name:     "embedding",
		Type:     schema.FieldTypeJson,
		Required: true,
	})
	form.Schema.AddField(&schema.SchemaField{
		Name:     "page_number",
		Type:     schema.FieldTypeNumber,
		Required: false,
	})
	form.Schema.AddField(&schema.SchemaField{
		Name:     "page_index",
		Type:     schema.FieldTypeNumber,
		Required: false,
	})
	filesColId, err := app.Dao().FindCollectionByNameOrId("files")
	if err != nil {
		fmt.Println(err)
	}
	form.Schema.AddField(&schema.SchemaField{
		Name:     "file",
		Type:     schema.FieldTypeRelation,
		Required: true,
		Options: &schema.RelationOptions{
			CollectionId:  filesColId.Id,
			CascadeDelete: true,
			MinSelect:     types.Pointer(1),
			MaxSelect:     types.Pointer(1),
		},
	})

	if err := form.Submit(); err != nil {
		fmt.Println(err)
		return err
	}
	return nil
}

func UpsertFileTable(app core.App) error {
	collectionName := "files"
	_, err := app.Dao().FindCollectionByNameOrId(collectionName)
	if err == nil {
		return nil
	}
	collection := &models.Collection{}
	form := forms.NewCollectionUpsert(app, collection)
	form.Name = collectionName
	form.Type = models.CollectionTypeBase
	form.ListRule = nil
	form.ViewRule = nil
	form.CreateRule = nil
	form.UpdateRule = nil
	form.DeleteRule = nil

	form.Schema.AddField(&schema.SchemaField{
		Name:     "name",
		Type:     schema.FieldTypeText,
		Required: true,
	})
	form.Schema.AddField(&schema.SchemaField{
		Name:     "url",
		Type:     schema.FieldTypeUrl,
		Required: false,
	})
	form.Schema.AddField(&schema.SchemaField{
		Name:     "file",
		Type:     schema.FieldTypeFile,
		Required: false,
		Options: &schema.FileOptions{
			MaxSelect: 1,
			MaxSize:   100000000,
		},
	})
	if err := form.Submit(); err != nil {
		fmt.Println(err)
		return err
	}
	return nil
}
