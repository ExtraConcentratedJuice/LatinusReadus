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
    let syntaxTree;
    let words = [];

    onMount(() => {
        const config = {
            namespace: "editor",
            onError: console.error,
        };

        editor = lex.createEditor(config);

        editor.setRootElement(readerDiv);

        editor.registerCommand(lex.SELECTION_CHANGE_COMMAND, () => {
            const selection = lex.$getSelection();

            if (selection.getNodes().length > 0) {
                words = [words.find(x => x.index === selection.getNodes()[0].index),
                 ...words.filter(x => x.index !== selection.getNodes()[0].index)];
            }            
        }, lex.COMMAND_PRIORITY_NORMAL);
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

            lex.$setSelection(lex.$createNodeSelection());

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
        <div class="sd-parse mb-4" id="syntax-tree" bind:this={syntaxTree}>
            Avunculus/NOUN meus/ADJ Miseni/PROPN erat/AUX classis/NOUN praefectus/VERB ./PUNCT Eo/DET die/NOUN ,/PUNCT quo/PRON tantae/DET cladis/NOUN initium/NOUN fuit/AUX ,/PUNCT avunculus/NOUN foris/ADV iacebat/VERB libris/NOUN que/CCONJ studebat/VERB ./PUNCT
            nsubj(Avunculus-1, Miseni-3)
            det(meus-2, Avunculus-1)
            ROOT(Miseni-3, Miseni-3)
            cop(erat-4, Miseni-3)
            nmod(classis-5, praefectus-6)
            nsubj(praefectus-6, Miseni-3)
            punct(.-7, Miseni-3)
            det(Eo-8, die-9)
            obl(die-9, iacebat-19)
            punct(,-10, initium-14)
            obl(quo-11, initium-14)
            amod(tantae-12, cladis-13)
            nmod(cladis-13, initium-14)
            nsubj(initium-14, iacebat-19)
            cop(fuit-15, initium-14)
            punct(,-16, initium-14)
            nsubj(avunculus-17, iacebat-19)
            advmod(foris-18, iacebat-19)
            ROOT(iacebat-19, iacebat-19)
            obl:arg(libris-20, studebat-22)
            cc(que-21, studebat-22)
            conj(studebat-22, iacebat-19)
            punct(.-23, iacebat-19)
            </div>
            
        <div class="content is-hidden" id="reader" bind:this={readerDiv} style="font-size:24px"></div>
        <div>
            <textarea style="width: 100%;" class="textarea is-large field" id="text-input" placeholder="Enter Latin text to analyze..." bind:this={textInput}></textarea>
            <button class="button is-large" on:click={submitText} bind:this={submitButton}>Analyze</button>
        </div>
    </div>
    <article class="message">
        {#each words as word}
        {#if word.pos !== "punctuation"}
        <div class="card mb-2">
            <header class="message-header">
            <p class="has-text-weight-bold">{word.word} (Lemm. {word.lemma})
            <br/><small class="has-text-weight-bold">{word.pos}</small>
            </p>
            </header>
            <div class="message-body">
            {#if word.features && Object.entries(word.features).length > 0}
            <div class="tags">
                {#if word.features.mood}
                <span class="tag is-info">{word.features.mood}</span>
                {/if}
                {#if word.features.case}
                <span class="tag is-info">{word.features.case}</span>
                {/if}
                {#if word.features.gender}
                <span class="tag is-info">{word.features.gender}</span>
                {/if}
                {#if word.features.number}
                <span class="tag is-info">{word.features.number}</span>
                {/if}
                {#if word.features.person}
                <span class="tag is-info">{word.features.person}</span>
                {/if}
                {#if word.features.tense}
                <span class="tag is-info">{word.features.tense}</span>
                {/if}
                {#if word.features.verbform}
                <span class="tag is-info">{word.features.verbform}</span>
                {/if}
                {#if word.features.voice}
                <span class="tag is-info">{word.features.voice}</span>
                {/if}
            </div>
            {/if}
            
            {#if word.parent !== -1}
            <p>Parent: {words.find(x => x.index === word.parent).word} ({word.parentRelation})</p>
            {/if}

            <p style="max-height:8em; overflow-y: auto;">{word.definition}</p>

            <!--

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
            -->
            </div>
        </div>
        {/if}
        {/each}
    </article>
</div>

</div>

