package functions

import (
	"context"
	"errors"
	"fmt"
	"io/ioutil"
	"math"
	"net/http"
	"github.com/k3a/html2text"
	"github.com/nlpodyssey/cybertron/pkg/tasks/textencoding"
	"github.com/tiktoken-go/tokenizer"
)

func Cosine(a []float64, b []float64) (cosine float64, err error) {
	count := 0
	length_a := len(a)
	length_b := len(b)
	if length_a > length_b {
		count = length_a
	} else {
		count = length_b
	}
	sumA := 0.0
	s1 := 0.0
	s2 := 0.0
	for k := 0; k < count; k++ {
		if k >= length_a {
			s2 += math.Pow(float64(b[k]), 2)
			continue
		}
		if k >= length_b {
			s1 += math.Pow(float64(a[k]), 2)
			continue
		}
		sumA += float64(a[k] * b[k])
		s1 += math.Pow(float64(a[k]), 2)
		s2 += math.Pow(float64(b[k]), 2)
	}
	if s1 == 0 || s2 == 0 {
		return 0.0, errors.New("s1 or s2 is zero")
	}
	return sumA / (math.Sqrt(s1) * math.Sqrt(s2)), nil
}

func GetUrlContents(url string, enc tokenizer.Codec) FileContents {
	//Getes the html in plain text
	res, err := http.Get(url)
	if err != nil {
		fmt.Println(err)
	}
	defer res.Body.Close()
	content, err := ioutil.ReadAll(res.Body)
	if err != nil {
		fmt.Println(err)
	}
	plain := html2text.HTML2Text(string(content))

	//Gets the tokens
	id, _, err := enc.Encode(plain)
	if err != nil {
		fmt.Println(err)
	}
	tokenCount := len(id)

	//Formats the output data
	var FileContents FileContents
	FileContents.Embeddings = append(FileContents.Embeddings, Embedding{Text: plain, PageNumber: 1, TokenCount: tokenCount})
	return FileContents
}

func (Payload *EmbeddingPayload) GetEmbedding(ctx context.Context, m textencoding.Interface) error {
	fmt.Println("encoding page", Payload.Text)
	vec, err := m.Encode(ctx, Payload.Text, 1)
	if err != nil {
		fmt.Print("error while embedding page", err)
	}
	vecResp := vec.Vector.Data().F64()
	Payload.Embedding = vecResp
	return nil
}

type Embedding struct {
	Text       string
	TokenCount int
	Embedding  []float32
	Model      string
	PageNumber int
	PageIndex  int
}

type FileContents struct {
	Embeddings []Embedding `json:"embeddings"`
}
