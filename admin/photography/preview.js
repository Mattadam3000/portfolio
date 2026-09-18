/* Use the public template for both saved photographs and unsaved CMS assets. */
(() => {
  const h = window.h;
  const escape = (value) =>
    String(value || "").replace(
      /[&<>"']/g,
      (c) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[c],
    );
  const template = fetch("/photography-template.html?fresh=" + Date.now(), {
    cache: "no-store",
  }).then((r) => {
    if (!r.ok) throw Error("Preview could not load");
    return r.text();
  });
  const PhotographyPreview = window.createClass({
    componentDidMount() {
      template
        .then((text) => {
          this.template = text;
          this.draw();
        })
        .catch((error) => {
          if (this.frame) this.frame.title = error.message;
        });
    },
    componentDidUpdate() {
      this.draw();
    },
    draw() {
      if (!this.template || !this.frame) return;
      const raw = this.props.entry.getIn(["data"]);
      const data =
        raw && typeof raw.toJS === "function" ? raw.toJS() : raw || {};
      const resolve = (path) => {
        if (!path) return "";
        const asset = this.props.getAsset(path);
        if (asset?.url) return asset.url;
        if (typeof asset === "string") return asset;
        if (/^(blob:|data:image\/|https:\/\/)/.test(path)) return path;
        return new URL(path, "https://mattadam.art/").href;
      };
      const slides = (data.projects || [])
        .filter((p) => p.published !== false)
        .map((project) => {
          let photos = [...(project.images || [])];
          if (project.cover) {
            const cover = photos.find((p) => p.image === project.cover) || {
              image: project.cover,
              alt: project.cover_alt || project.title,
            };
            photos = [
              cover,
              ...photos.filter((p) => p.image !== project.cover),
            ];
          }
          if (!photos.length) photos = [{}];
          return `<section class="slide" id="${escape(project.slug)}" data-project="${escape(project.slug)}"><div class="collection-track">${photos
            .map((photo, i) => {
              const path = resolve(photo.image);
              return `<div class="photo-slide" role="group" aria-label="Photograph ${i + 1} of ${photos.length}">${path ? `<img src="${escape(path)}" alt="${escape(photo.alt || project.title)}" loading="lazy">` : "<span>Choose a photograph</span>"}<div class="caption"><div class="project-label"><span>${escape(project.title)}</span><span class="description">${escape(photo.caption || project.description)}</span></div></div></div>`;
            })
            .join("")}</div></section>`;
        })
        .join("");
      const values = {
        MODE: "portfolio",
        START: "",
        TITLE: "Photography preview",
        DESCRIPTION: "",
        CANONICAL: "",
        BACK: "",
        CONTACT_URL: "#",
        CONTACT_LABEL: escape(data.contact_label || "Contact"),
        SLIDES:
          slides ||
          '<section class="slide empty">Add photographs to preview.</section>',
      };
      const doc = this.frame.contentDocument;
      doc.open();
      doc.write(
        this.template
          .replace(/{{(\w+)}}/g, (_, key) => values[key] || "")
          .replace(
            "</body>",
            '<script>document.addEventListener("click",e=>{if(e.target.closest("a"))e.preventDefault()})<\/script></body>',
          ),
      );
      doc.close();
    },
    render() {
      return h("iframe", {
        title: "Photography preview",
        ref: (node) => {
          this.frame = node;
        },
        style: {
          width: "100%",
          height: "100vh",
          border: 0,
          display: "block",
          background: "#fff",
        },
      });
    },
  });
  window.CMS.registerPreviewTemplate("photography", PhotographyPreview);
})();
