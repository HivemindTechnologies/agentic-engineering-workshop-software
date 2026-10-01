.PHONY: run watch build html pdf stop check new-lesson

# Which spine, deck-$(deck).md: make pdf deck=software-part2. Default is software Part 1.
deck ?= software-part1

# Assemble and serve one deck with live reload on $PORT (default 8000).
run: build
	./.bin/present $(deck)

# Like run, but also rebuild on edits to the spine or lessons/*.md (needs entr).
watch:
	./.bin/watch $(deck)

# Assemble every deck*.md into .build/.
build:
	./.bin/build-deck

# Self-contained static site in dist/$(deck)/.
html:
	./.bin/export-html $(deck)

# workshop-$(deck).pdf via headless Chromium.
pdf:
	./.bin/export-pdf $(deck)

# Free the serve port.
stop:
	./.bin/stop

# CI gate: lesson contract, every deck builds, static export, no local paths.
check:
	./.bin/check

# make new-lesson id=<id> name="<Name>" [title="<Full Title>"]
new-lesson:
	./.bin/new-lesson "$(id)" "$(name)" "$(title)"
