<script>
	import lex from 'lexical';
	import { createEventDispatcher } from 'svelte';
	import { onMount } from 'svelte';
	import { parse } from 'svelte/compiler';

	let readerDiv;
	let submitButton;
	let textInput;
	let editor;
	let syntaxTree;
	let syntaxTreeContainer;
	let parsedSentence;
	let words = [];

	onMount(() => {
		const config = {
			namespace: 'editor',
			onError: console.error
		};

		editor = lex.createEditor(config);

		editor.setRootElement(readerDiv);

		editor.registerCommand(
			lex.SELECTION_CHANGE_COMMAND,
			() => {
				const selection = lex.$getSelection();
				lex.$getCharacterOffsets;
				console.log(selection);

				if (selection.getNodes().length > 0) {
					console.log(selection.getNodes());
					words = [
						words.find((x) => x.index === selection.getNodes()[0].word.index),
						...words.filter((x) => x.index !== selection.getNodes()[0].word.index)
					];

					let nodeIndex = selection.getNodes()[0].word.index;

					console.log(nodeIndex);

					if (
						nodeIndex < parsedSentence[0].index ||
						nodeIndex > parsedSentence[parsedSentence.length - 1].index
					) {
						parsedSentence = getSentence(nodeIndex);
						syntaxTree.innerHTML = buildSd(words, parsedSentence);
						Annodoc.activate(Config.bratCollData, Collections.listing);
					}
				}
			},
			lex.COMMAND_PRIORITY_NORMAL
		);
	});

	function getSentence(sentenceWordIndex) {
		let word = words.find((x) => x.index === sentenceWordIndex);
		if (word == null) return null;

		let sentence = [];
		sentence.push(word);
		while (
			word.index > 0 &&
			(word = words.find((x) => x.index === word.index - 1)) != null &&
			(word.pos != 'punctuation' || word.word != '.')
		) {
			sentence = [word, ...sentence];
		}
		word = words.find((x) => x.index === sentenceWordIndex);
		while (
			(word = words.find((x) => x.index === word.index + 1)) != null &&
			(word.pos != 'punctuation' || word.word != '.')
		) {
			sentence.push(word);
		}

		if (word != null && word.pos == 'punctuation' && word.word == '.') {
			sentence.push(word);
		}

		return sentence;
	}

	function titleCase(string) {
		return string[0].toUpperCase() + string.slice(1).toLowerCase();
	}

	function buildSd(allWords, sentence) {
		let sd = '';
		for (let word of sentence) {
			let features = '';
			if (Object.entries(word.features).length > 0) {
				features = `[${Object.entries(word.features)
					.map((x) => `${titleCase(x[0])}=${x[1].map(x => titleCase(x)).join(",")}`)
					.join('|')}]`;
			}
			sd += `${word.word}/${word.upos}${features} `;
		}
		sd += '\n';
		let lowIndex = sentence[0].index;
		for (let word of sentence) {
			if (word.parentRelation == 'ROOT' || word.parentRelation == 'punct') continue;

			sd += `${word.parentRelation}(${word.word}-${word.index - lowIndex + 1}, ${allWords.find((x) => x.index === word.parent).word}-${word.parent - lowIndex + 1})\n`;
		}
		console.log(sd);
		return sd;
	}

	function updateAnalysis(analysis) {
		words = analysis;
		editor.update(() => {
			function makeWord(word) {
				const node = lex.$createTextNode(word.word);
				node.toggleUnmergeable();
				node.word = word;
				return node;
			}

			const root = lex.$getRoot();

			root.clear();

			const paragraph = lex.$createParagraphNode();

			for (let i = 0; i < analysis.length; i++) {
				const word = analysis[i];

				if (word.pos === 'punctuation') {
					paragraph.append(makeWord(word));
				} else {
					if (i !== 0) {
						paragraph.append(lex.$createTextNode(' '));
					}
					paragraph.append(makeWord(word));
				}
			}

			root.append(paragraph);
			readerDiv.classList.remove('is-hidden');
			parsedSentence = getSentence(12);
			syntaxTree.innerHTML = buildSd(words, parsedSentence);
			Annodoc.activate(Config.bratCollData, Collections.listing);
			syntaxTreeContainer.hidden = false;
		});
	}

	async function submitText() {
		//submitButton.disabled = true;
		submitButton.classList.add('is-loading');

		const resp = await fetch('http://127.0.0.1:5000/analyze', {
			headers: new Headers({ 'content-type': 'application/json' }),
			method: 'POST',
			body: JSON.stringify({ text: textInput.value })
		});

		submitButton.classList.remove('is-loading');
		//submitButton.disabled = false;

		const analysis = await resp.json();
		updateAnalysis(analysis);
	}
</script>

<div class="container">
	<h1 class="title is-size-1 mt-4" style="font-family: 'Cinzel Decorative', serif;">
		Latinus Readus
	</h1>
	<div class="columns">
		<div class="column is-three-quarters">
			<div hidden="true" bind:this={syntaxTreeContainer}>
				<div class="sd-parse mb-4" id="syntax-tree" bind:this={syntaxTree}></div>
			</div>

			<div class="content is-hidden" id="reader" bind:this={readerDiv} style="font-size:26px"></div>
			{#if words.length > 0}
				<hr />
			{/if}
			<div>
				<textarea
					style="width: 100%;border: none transparent;border-color: transparent;outline: none; border-radius: 0px;"
					class="textarea is-large field"
					id="text-input"
					placeholder="Enter Latin text to analyze..."
					bind:this={textInput}
				></textarea>
				<button
					class="button is-large mt-4"
					style="border-radius: 0px;"
					on:click={submitText}
					bind:this={submitButton}>Analyze</button
				>
			</div>
		</div>
		<article class="message">
			{#each words as word}
				{#if word.pos !== 'punctuation'}
					<div class="card mb-2">
						<header class="message-header">
							<p class="has-text-weight-bold">
								{word.word} (Lemm. {word.lemma})
								<br /><small class="has-text-weight-bold"
									><a href="https://universaldependencies.org/u/pos/{word.upos}">{word.pos}</a
									></small
								>
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

							<p style="max-height:8em; overflow-y: auto;">{word.definition}</p>
							{#if word.parent !== -1}
								<p class="mt-2">
									Parent: {words.find((x) => x.index === word.parent).word} (<a
										href="https://universaldependencies.org/u/dep/{word.parentRelation.replace(
											':',
											'-'
										)}">{word.parentRelation}</a
									>)
								</p>
							{/if}
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

<style>
	* {
		font-family: 'Cinzel', serif;
	}
</style>
