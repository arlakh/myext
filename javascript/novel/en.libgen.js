
class DefaultExtension extends MProvider {
  getHeaders(url) {
    return {
      "User-Agent": "Mozilla/5.0"
    };
  }

  mangaListFromPage(doc) {
    const list = [];
    const rows = doc.select("table.c > tbody > tr");

    for (let i = 1; i < rows.length; i++) {
      const cols = rows[i].select("td");
      const name = cols[2]?.text.trim() ?? "Untitled";
      const link = cols[9]?.selectFirst("a")?.getHref;
      const imageUrl = "https://raw.githubusercontent.com/kodjodevf/mangayomi-extensions/main/javascript/icon/en.libgen.png";

      if (link && cols[8]?.text.toLowerCase().includes("epub")) {
        list.push({ name, link, imageUrl });
      }
    }

    const hasNextPage = doc.selectFirst("a[title='Next page']") !== null;
    return { list, hasNextPage };
  }

  async getPopular(page) {
    const url = `${this.source.baseUrl}/search.php?req=&res=25&sort=year&sortmode=DESC&page=${page}&format=epub`;
    const res = await new Client().get(url, this.getHeaders());
    const doc = new Document(res.body);
    return this.mangaListFromPage(doc);
  }

  async getLatestUpdates(page) {
    return await this.getPopular(page);
  }

  async search(query, page, filters) {
    const url = `${this.source.baseUrl}/search.php?req=${encodeURIComponent(query)}&res=25&sort=year&sortmode=DESC&page=${page}&format=epub`;
    const res = await new Client().get(url, this.getHeaders());
    const doc = new Document(res.body);
    return this.mangaListFromPage(doc);
  }

  guessGenreFromTitle(title) {
    const lower = title.toLowerCase();
    const genres = [];
    if (lower.includes("romance") || lower.includes("love")) genres.push("Romance");
    if (lower.includes("magic") || lower.includes("sorcery")) genres.push("Fantasy");
    if (lower.includes("murder") || lower.includes("crime") || lower.includes("detective")) genres.push("Mystery");
    if (lower.includes("future") || lower.includes("robot") || lower.includes("alien")) genres.push("Science Fiction");
    if (lower.includes("war") || lower.includes("battle")) genres.push("Action");
    if (lower.includes("life")) genres.push("Slice of Life");
    if (lower.includes("school")) genres.push("School");
    return genres;
  }

  async getDetail(url) {
    const client = new Client();
    const res = await client.get(url, this.getHeaders());
    const doc = new Document(res.body);

    const name = doc.selectFirst("h1")?.text.trim() ?? "Unknown Title";
    const description = doc.selectFirst("body")?.text.slice(0, 400) ?? "";
    const author = doc.select("td:contains('Author') + td")?.text ?? "Unknown";
    const status = 1;
    const genre = this.guessGenreFromTitle(name);

    const finalLink = doc.selectFirst("a[href$='.epub']")?.getHref ?? null;
    if (!finalLink) {
      return {
        description,
        genre,
        author,
        status,
        chapters: [],
      };
    }

    const book = await parseEpub(name, finalLink, this.getHeaders());
    const chapters = book.chapters.map(ch => ({
      name: ch,
      url: finalLink + ";;;" + ch,
      dateUpload: String(Date.now()),
      scanlator: null,
    }));

    return {
      description,
      genre,
      author,
      status,
      chapters,
    };
  }

  async getHtmlContent(name, url) {
    const [bookUrl, chapterTitle] = url.split(";;;");
    return await parseEpubChapter(name, bookUrl, this.getHeaders(), chapterTitle);
  }

  async cleanHtmlContent(html) {
    return html;
  }

  getFilterList() {
    return [];
  }

  getSourcePreferences() {
    throw new Error("getSourcePreferences not implemented");
  }
}
