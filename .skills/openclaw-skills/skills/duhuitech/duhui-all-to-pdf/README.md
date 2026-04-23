# duhui-all-to-pdf

一个用于通过阿里云市场度慧接口，把单个本地文件转换为 PDF 的轻量Skill。

A lightweight skill for converting a single local file to PDF through the Duhui API on Alibaba Cloud Marketplace.

## 能力范围 / What This Skill Does

- 把单个本地文件转换为单个 PDF。
- 走度慧的 `v2/convert_async` 异步接口，而不是本地转换器。
- 支持常见 Office、WPS、OFD、图片、文本、HTML/Markdown 等本地文件输入。
- 支持通过 `--extra-params` 透传 vendor `v2` 参数。

- Converts one local source file into one PDF.
- Uses Duhui's `v2/convert_async` API instead of a local converter.
- Supports common local Office, WPS, OFD, image, text, HTML, and Markdown inputs.
- Allows vendor-specific `v2` parameters through `--extra-params`.

### 支持的文件类型 / Supported File Types

| 类型 / Category | 扩展名 / Extensions |
| --- | --- |
| PDF | `pdf` |
| Microsoft Office | `doc`, `docx`, `ppt`, `pptx`, `xls`, `xlsx`, `pot`, `pps`, `ppsx`, `csv` |
| WPS | `wps`, `wpt`, `dps`, `dpt`, `et`, `ett` |
| Apple iWork | `pages`, `key`, `numbers` |
| OFD | `ofd` |
| E-publication | `caj`, `nh`, `kdh` |
| E-book | `epub`, `chm`, `mobi`, `azw`, `azw3`, `fb2`, `cbr`, `cbz`, `djvu` |
| Markdown | `md` |
| SVG | `svg` |
| CAD | `dwg`, `dxf`, `dwt`, `dws` |
| Sketch | `sketch` |
| Web files | `html`, `htm`, `mht`, `eml` |
| Images | 几乎所有图片格式 `png`, `jpg`, `jpeg`, `gif`, `tif`, `tiff`, `bmp`, `webp`, `ai`; `type` 等 |
| Text and code files | `txt`, `rtf`, `java`, `js`, `c`, `cpp`, `jsp`, `css`, `xml`, `properties`, `log`; `type` 等 |

## 兼容性 / Compatibility

- 脚本层是通用的：任何支持执行命令的 coding 工具、AI agent 或自动化流程都可以直接调用。

- The script layer is tool-agnostic: any coding tool, AI agent, or automation flow that can run commands can call it directly.

## 安装方式 / Installation

### 方式一：用 `npx` 安装 / Option 1: Install with `npx`

如果你的环境支持 `skills` CLI，可以直接运行：

If your environment supports the `skills` CLI, you can install the skill with:

```bash
npx skills add https://github.com/duhuitech/all-to-pdf --skill duhui-all-to-pdf
```

安装后，skill 会在兼容的 agent 环境中可用。

After installation, the skill will be available in compatible agent environments.

### 方式二：agent里直接安装 Skill / Option 2: Install the Skill Directly in Your Agent

安装 Skill：https://github.com/duhuitech/all-to-pdf

Install the skill directly from GitHub: https://github.com/duhuitech/all-to-pdf

## 前置条件 / Requirements

- Python 3
- 度慧文档转 PDF 的 AppCode
- 一个本地输入文件

- Python 3
- An AppCode for the Duhui document-to-PDF service
- A local input file

需提供AppCode，可从阿里云市场对应商品页免费获取：

You can get the AppCode from the Alibaba Cloud Marketplace product page:

- [度慧文档转PDF / Duhui Document to PDF](https://market.aliyun.com/detail/cmapi00044564)

## 使用方式 / Usage

当请求中明确出现下面这类意图时，这个 skill 被触发：

This skill is a good fit when the request clearly matches intents like these:

- 提到“文档转 PDF”“文档转换”“格式转换”“PDF 转换”
- 要把单个本地 `doc/docx/ppt/pptx/xls/xlsx/ofd/img/txt/html/md/...` 文件转成 PDF

- Mentions "Duhui", "document to PDF", "document conversion", "format conversion", or "PDF conversion"
- Needs to convert a single local `doc/docx/ppt/pptx/xls/xlsx/ofd/img/txt/html/md/...` file to PDF

## 支持参数 / Supported `v2/convert_async` Parameters

这个 skill 对 `v2/convert_async` 的参数支持方式如下：

This skill exposes `v2/convert_async` parameters in the following way:

- 通过 `--extra-params` 以 JSON object 透传

- Other supported fields can be forwarded through `--extra-params` as a JSON object

示例：

Example:

```bash
python3 scripts/duhui_doc_to_pdf.py ./input.docx --extra-params '{"compress":2,"linearization":1}'
```


### 输出 PDF 相关 / PDF Output

| 参数 / Param | 类型 / Type | 说明 |
| --- | --- | --- |
| `linearization` | int | 是否启用快速 web 显示，`0/1` |
| `compress` | int | PDF 压缩级别，`0` 不压缩，`1/2/3` 压缩率递增 |
| `flatten` | int | 是否扁平化，把注释等内容合并进 PDF，`0/1` |
| `imagepdf` | int | 是否输出图片型 PDF，`0/1` |
| `pagesize` | int | 页面大小，常见值：`1:A3` `2:A4` `3:A5` `4:B4` `5:B5` `6:Letter` `7:Legal` `8:Tabloid` `9:Ledger` |
| `adjustorientation` | int | 调整页面方向；常见值：`1/2` 调成竖屏，`3/4` 调成横屏 |
| `pageorientation` | int | 页面横竖方向；常见值：`1` 横向，`2` 纵向 |
| `pagesplit` | int | 按长边拆页，常见值：`2/3` |
| `needpagesizeinfo` | int | 是否返回每页尺寸信息，`0/1` |
| `pdffilename` | string | 服务端生成 PDF 的文件名 |

### Word / Excel / HTML / 文本相关 / Word, Excel, HTML, Text

| 参数 / Param | 类型 / Type | 说明 |
| --- | --- | --- |
| `wordshowmarkup` | int | Word 是否显示审阅标记，`0/1` |
| `excelislandscape` | int | Excel 是否横向排版，`0/1` |
| `exceliscenter` | int | Excel 是否横竖居中，`0/1` |
| `excelmargin` | int | Excel 四边边距，单位像素 |
| `excelsheetindex` | int | 指定 Excel 转换的 Sheet；`0` 常表示全部 |
| `excelnotshowgridlines` | int | Excel 是否隐藏网格线，`0/1` |
| `exceluseprintarea` | int | Excel 是否使用打印区域 |
| `excelpagesize` | int | Excel 页面大小，取值体系与 `pagesize` 类似 |
| `htmloutline` | int | HTML 是否根据 `h1/h2/...` 生成 outline，`0/1` |

### PowerPoint 相关 / PowerPoint

| 参数 / Param | 类型 / Type | 说明 |
| --- | --- | --- |
| `powerpointoutputtype` | int | PPT 输出样式；`0` 常表示幻灯片，`1-6` 为不同讲义模式 |
| `powerpointhandoutorder` | int | 讲义模式顺序；常见值：`0` 水平，`1` 垂直 |
| `powerpointhandoutorientation` | int | 讲义输出方向；常见值：`1` 横向，`2` 纵向 |

### 图片 / OCR 相关 / Image and OCR

| 参数 / Param | 类型 / Type | 说明 |
| --- | --- | --- |
| `ocr` | int | 是否启用 OCR，`0/1` |
| `deskew` | int | 是否矫正倾斜文字，`0/1` |
| `clean` | int | 是否清除图像背景只保留文字，`0/1` |
| `grayimage` | int | 是否转灰度图，`0/1` |
| `text` | int | OCR 后是否用矢量文字替换图片中文字，`0/1` |
| `split2p` | int | OCR 场景下横向图片是否拆成两页，`0/1` |
| `imagesize` | int | 统一每页宽度；设置后通常会覆盖部分页面尺寸行为 |
| `language` | int | OCR 识别语言，常见值：`1` 英语，`2` 简体中文，`3` 繁体中文，`8` 日文，`9` 韩文 |
| `dewarp` | int | 是否切边矫正，`0/1`；开启时通常要求一次只传一张图 |

### 网页 URL 相关 / Web URL

| 参数 / Param | 类型 / Type | 说明 |
| --- | --- | --- |
| `ismobileurl` | int | 当 `type=url/html/md` 时，是否按移动端网页抓取，`0/1` |
| `urldesktopwidth` | int | 当 `type=url/html/md` 时，桌面端网页最大宽度 |
| `htmlpagemargin` | string | 当 `type=url/html/md` 时，输出页面边距字符串 |
| `urlwait` | int | 当 `type=url` 时，抓取前额外等待的秒数 |
| `urltimeout` | int | 当 `type=url` 时，加载资源的超时时间 |
| `urlonepage` | int | 当 `type=url/html/md` 时，是否生成单页长 PDF，`0/1` |

### EPUB 相关 / EPUB

| 参数 / Param | 类型 / Type | 说明 |
| --- | --- | --- |
| `epubfontsize` | int | EPUB 输出字体大小 |
| `epublineheight` | int | EPUB 输出行高百分比 |
| `epubpagesize` | string | EPUB 自定义页面大小；设置后通常会覆盖 `pagesize` |
| `epubmargin` | string | EPUB 输出页面边距 |

### 密码 / 权限 / 水印 / Passwords, Permissions, Watermark

| 参数 / Param | 类型 / Type | 说明 |
| --- | --- | --- |
| `password` | string | 源文件密码，适用于有密码的 PDF/Word/PPT/Excel |
| `userpassword` | string | 打开生成 PDF 所需密码 |
| `ownerpassword` | string | 修改生成 PDF 所需密码 |
| `pdfrestriction` | string | PDF 权限，示例：`010` |
| `watermark` | string | 水印文本 |
| `watermarkfontsize` | int | 水印字体大小 |
| `watermarkfontcolor` | string | 水印颜色，通常是 7 位颜色码 |
| `watermarkfontalpha` | int | 水印透明度 |
| `watermarkstyle` | int | 水印样式；常见值：`0` 单个，`1` 铺满 |

### CAD 相关 / CAD

| 参数 / Param | 类型 / Type | 说明 |
| --- | --- | --- |
| `cadlayer` | int | CAD 是否生成图层信息，`0/1` |
| `cadisdisplay` | int | CAD 是否按 Display 显示，`0/1` |
| `cadquality` | int | CAD 输出品质，常见范围 `1-5` |
| `caddetectempty` | int | CAD 是否删除空页，`0/1` |
