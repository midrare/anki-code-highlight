# anki-code-highlight

**Code highlighting for Anki.**

![Screenshot](screen.png)  


## Getting Started

### Prerequisites
 
  1. Go to Anki -> Tools (menubar) -> Add-ons -> Install from file  
  2. Select file downloaded from releases page  

## Usage
In the note editor, click the `<>` button and enclose your code in `<pre><code> ... </code></pre>`. In the previewer and reviewer, code highlighting will be applied automatically.

By default, the programming language is auto-detected. You can manually specify the language editing the `class` attribute e.g. `<code class="language-cpp">`. Look in `highlightjs/languages` for the list of language codes you can choose from.  Consider doing this if auto-detecting takes too long (makes the reviewer lag).

*anki-code-highlight* is non-invasive; it doesn't modify your original note to add the highlighting. If you disable or uninstall *anki-code-highlight*, your `pre code` blocks just return to being normal `pre code` blocks.

You can change the font size in the config file. Any valid [CSS font-size property](https://www.w3schools.com/css/css_font_size.asp) is valid in this field.

The color scheme can changed by setting the config file. Look in `highlightjs/styles` for the list of color schemes you can choose from.

## License
Distributed under the MIT license. See `LICENSE.txt` for more information


## Acknowledgements
Uses [highlight.js](https://highlightjs.org/), included under the BSD 3-Clause license. See `highlightjs/LICENSE` file for license details.
