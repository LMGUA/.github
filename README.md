# LMGUA 组织主页 · Organization profile

[LMGUA · 薄肌全球高校联盟](https://github.com/LMGUA)的 GitHub 组织主页文案与公开展示素材。

The public community profile and display assets for LMGUA.

这个 GitHub 组织是 **LMGUA 官方开发者社区**。本仓库维护组织介绍与公开品牌素材；开发者留名和项目交流见 [developers](https://github.com/LMGUA/developers)。

This GitHub organization is the **official LMGUA developer community**. This repository maintains its profile and public brand assets. See [developers](https://github.com/LMGUA/developers) to introduce yourself and share projects.

- [简体中文 · 组织主页](profile/README.md)
- [English · Organization profile](profile/README.en.md)

GitHub 从 `profile/README.md` 展示组织主页，默认使用简体中文。英文版本位于 `profile/README.en.md`，修改介绍时请同步更新两种语言。

GitHub displays `profile/README.md` on the organization overview, with Simplified Chinese as the default. Please keep both language versions in sync.

公开横幅位于 `profile/assets/lmgua-banner-slogan.svg`：左侧为红色屈臂图形替代 G 的 LMGUA 组合字标，logo 正下方以小字标注“薄肌全球高校联盟 · 官方开发者社区”；右侧为两行大字——白色“如果你不练薄肌”、红色“那我不要和你说话”。横幅在 GitHub 深浅主题中均使用墨黑背景，文字已转为矢量轮廓；点击横幅进入 [lmgua.org](https://lmgua.org/)。

The public banner places the integrated LMGUA wordmark on the left, with 薄肌全球高校联盟 · 官方开发者社区 in small type directly below it. Two large Chinese slogan lines sit on the right, in white and red. Both profiles keep its dark background in all GitHub themes. All lettering uses vector outlines, and the banner links to [lmgua.org](https://lmgua.org/).

README 最上方是一排统一尺寸的按钮，从左到右为[邵艾伦 Alan 的 X](https://x.com/AlanShao111)、[Discord](https://discord.gg/vfB4G7KXdx)、[官方网站](https://lmgua.org/)。X 使用黑底白字与红边框，Discord 使用红底白字，官网使用白底红字；按钮尺寸均为 244 × 52，素材为 `profile/assets/community-{x,discord,website}-{zh,en}.svg`。下方保留 logo 横幅，开发者社区定位直接排在 logo 下方，不再单设标题。

The top row contains matching 244 × 52 buttons in this order: Alan Shao’s X, Discord, and the official website. Use white on black with a red border for X, white on red for Discord, and red on white for the website. Keep the logo banner below, with the developer-community subtitle inside the artwork rather than a separate heading. Both language versions share this layout.

默认头像使用[红色图形、纯白背景](profile/assets/avatar-light.png)。深色头像保留为备选。

The default avatar uses the [red symbol on pure white](profile/assets/avatar-light.png). The dark avatar remains an alternative.

按钮母版包括 `source/icons/` 与 `source/community-button-labels.json`。安装 Python `fontTools` 和 librsvg 后，运行 `python scripts/build-community-buttons.py` 可重建六个 SVG；常规构建无需字体文件。

Button sources live in `source/icons/` and `source/community-button-labels.json`. With Python `fontTools` and librsvg installed, run `python scripts/build-community-buttons.py` to rebuild all six SVGs without font files.
