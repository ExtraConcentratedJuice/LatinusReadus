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
        });
    }

    async function submitText() {
        submitButton.disabled = true;

        const resp = await fetch("http://127.0.0.1:5000/analyze", {
            headers: new Headers({'content-type': 'application/json'}),
            method: "POST",
            body: JSON.stringify({"text": textInput.value})
        })

        submitButton.disabled = false;

        const analysis = await resp.json();
        updateAnalysis(analysis);
    }

</script>

<div class="pure-g">
    <div class="pure-u-2-3">
        <div id="reader" bind:this={readerDiv} style="font-family: 'Cinzel', serif;  font-size:22px"></div>
        <div>
            <textarea id="text-input" placeholder="Enter Latin text to analyze..." bind:this={textInput}></textarea>
            <button on:click={submitText} bind:this={submitButton}>Analyze</button>
        </div>
    </div>
    <div class="pure-u-1-3">
        {#each words as word}
        {#if word.pos !== "punctuation"}
        <div>
            <p>Part of Speech: {word.pos}</p>
            <p>Word: {word.word}</p>
            <p>Lemma: {word.lemma}</p>
            <p>Features</p>
            <ul>
                {#each Object.entries(word.features) as [name, val]}
                <li>{name}: {val}</li>
                {/each}
            </ul>
        </div>
        <hr>
        {/if}
        {/each}
    </div>
</div>
