<style>
    * {
    font-family: 'Cinzel', serif; 

    }
</style>
<script>
    import lex from "lexical";
	import { createEventDispatcher } from "svelte";
	import { onMount } from "svelte";

    let readerDiv;
    let submitButton;
    let textInput;
    let editor;
    let words = [];

    onMount(() => {

        const config = {
            namespace: "editor",
            onError: console.error,
        };

        editor = lex.createEditor(config);

        editor.setRootElement(readerDiv);
    })


    function updateAnalysis(analysis) {
        words = analysis;
        editor.update(() => {
            function makeWord(word) {
                const node = lex.$createTextNode(word.word);
                node.word = word;
                return node
            }

            const root = lex.$getRoot();

            root.clear();

            const paragraph = lex.$createParagraphNode();

            for (let i = 0; i < analysis.length; i++) {
                const word = analysis[i];

                if (word.pos === "punctuation") {
                    paragraph.append(makeWord(word));
                } else {
                    if (i !== 0) {
                        paragraph.append(lex.$createTextNode(" "));
                    }
                    paragraph.append(makeWord(word));
                }
            }
            root.append(paragraph);
            readerDiv.classList.remove("is-hidden");
        });
    }

    async function submitText() {
        //submitButton.disabled = true;
        submitButton.classList.add("is-loading");

        const resp = await fetch("http://127.0.0.1:5000/analyze", {
            headers: new Headers({'content-type': 'application/json'}),
            method: "POST",
            body: JSON.stringify({"text": textInput.value})
        })

        submitButton.classList.remove("is-loading");
        //submitButton.disabled = false;

        const analysis = await resp.json();
        updateAnalysis(analysis);
    }

</script>
<div class="container">
<h1 class="title is-size-1 mt-4" style="font-family: 'Cinzel Decorative', serif;">Latinus Readus</h1>
<div class="columns">
    <div class="column is-three-quarters">
        <div class="content is-hidden" id="reader" bind:this={readerDiv} style="font-size:24px"></div>
        <div>
            <textarea style="width: 100%;" class="textarea is-large field" id="text-input" placeholder="Enter Latin text to analyze..." bind:this={textInput}></textarea>
            <button class="button is-large" on:click={submitText} bind:this={submitButton}>Analyze</button>
        </div>
    </div>
    <div class="column">
        {#each words as word}
        {#if word.pos !== "punctuation"}
        <div class="box">
            <h3 class="has-text-weight-bold">{word.word}</h3>

            <div class="tags">
                <span class="tag is-info">{word.pos}</span>
                {#if word.features.case}
                <span class="tag is-info">{word.features.case}</span>
                {/if}
                {#if word.features.gender}
                <span class="tag is-info">{word.features.gender}</span>
                {/if}
                {#if word.features.number}
                <span class="tag is-info">{word.features.number}</span>
                {/if}
            </div>
            <p>{word.definition}</p>

            <p>Lemma: {word.lemma}</p>
            <p>Features</p>
            <ul>
                {#each Object.entries(word.features) as [name, val]}
                <li>{name}: {val}</li>
                {/each}
            </ul>
            {#if word.category}
            <p>Category</p>
            <ul>
                {#each Object.entries(word.category) as [name, val]}
                <li>{name}: {val}</li>
                {/each}
            </ul>
            {/if}

        </div>
        <hr>
        {/if}
        {/each}
    </div>
</div>

</div>

