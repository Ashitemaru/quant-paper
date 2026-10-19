# Model logos

Brand logos from the MIT-licensed [LobeHub lobe-icons collection](https://github.com/lobehub/lobe-icons).
Pinned upstream commit: `8a1b2821bb768c484fe8da20c5e1838b6bf551a9`.

The original SVG geometry and brand colors are retained. Each viewBox is padded from 24×24 to 28×28 with a 2-unit margin, translated without stretching, and exported to a transparent 21×21 pt vector PDF. `currentColor` becomes black. No raster images are embedded.

GLM uses the Z.ai provider mark. GPT uses the OpenAI provider mark. These marks identify the corresponding model families; they are not claims of endorsement. Logo and trademark rights remain with their owners.

| Paper asset | Upstream source | Original SHA-256 |
|---|---|---|
| `claude.svg`, `claude.pdf` | [claude-color.svg](https://raw.githubusercontent.com/lobehub/lobe-icons/8a1b2821bb768c484fe8da20c5e1838b6bf551a9/packages/static-svg/icons/claude-color.svg) | `a3101f3047a119aa11825ad9369510f0c472428c8c52d420e31bc62db44a8364` |
| `openai.svg`, `openai.pdf` | [openai.svg](https://raw.githubusercontent.com/lobehub/lobe-icons/8a1b2821bb768c484fe8da20c5e1838b6bf551a9/packages/static-svg/icons/openai.svg) | `a595df6b423920c67a7f8f73c063e4bfb72d415948097b6cac063a2366bb5186` |
| `gemini.svg`, `gemini.pdf` | [gemini-color.svg](https://raw.githubusercontent.com/lobehub/lobe-icons/8a1b2821bb768c484fe8da20c5e1838b6bf551a9/packages/static-svg/icons/gemini-color.svg) | `8ab0a9bafec11f7e69bcb9fc4ffd8f1bc927d1ddcbbb6ff36dee5ae8b5a9d602` |
| `deepseek.svg`, `deepseek.pdf` | [deepseek-color.svg](https://raw.githubusercontent.com/lobehub/lobe-icons/8a1b2821bb768c484fe8da20c5e1838b6bf551a9/packages/static-svg/icons/deepseek-color.svg) | `deba5f98a5c1796e20fcac3149bcd7eb8a32f0bdd04d048819400b1f28bd1439` |
| `kimi.svg`, `kimi.pdf` | [kimi.svg](https://raw.githubusercontent.com/lobehub/lobe-icons/8a1b2821bb768c484fe8da20c5e1838b6bf551a9/packages/static-svg/icons/kimi.svg) | `ed08131b46acf70e6e2144eceb775e74098b58ea65fa21eaee04be7b05cfe63b` |
| `glm.svg`, `glm.pdf` | [zai.svg](https://raw.githubusercontent.com/lobehub/lobe-icons/8a1b2821bb768c484fe8da20c5e1838b6bf551a9/packages/static-svg/icons/zai.svg) | `e748cb5108ce37b116d7a5ba97d37e0ae97eadf6849b0de11afb248e244a01e1` |

The original MIT license is preserved in `LICENSE-lobe-icons.txt`.

Rebuild with Python and CairoSVG: `python build.py --output-dir /path/to/quant-paper/assets/model-logos`.

Recommended LaTeX size: `height=1.05em`, baseline adjustment `-0.18em`, followed by `\hspace{0.3em}`. All boxes are equal and transparent.

The contact sheet shows large color logos, 20/28 px small-size recognition, and grayscale silhouettes.
