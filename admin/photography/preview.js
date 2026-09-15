/* Photography-specific Sveltia preview. getAsset includes unsaved image uploads. */
(() => {
  const h = window.h;
  const PhotographyPreview = window.createClass({
    getInitialState() { return { projectIndex: null }; },
    render() {
      const raw = this.props.entry.getIn(['data']);
      const data = raw && typeof raw.toJS === 'function' ? raw.toJS() : raw || {};
      const projects = (data.projects || []).filter(p => p.published !== false);
      const active = projects[this.state.projectIndex];
      const resolve = path => {
        if (!path) return '';
        const asset = this.props.getAsset(path);
        if (asset && asset.url) return asset.url;
        if (typeof asset === 'string') return asset;
        if (/^(blob:|data:image\/|https:\/\/)/.test(path)) return path;
        return new URL(path, 'https://mattadam.art/').href;
      };
      const slides = active
        ? (active.images || []).map((photo, index) => ({ project: active, photo, index }))
        : projects.map((project, index) => ({ project, index, photo: project.cover
            ? { image: project.cover, alt: project.cover_alt || project.title }
            : (project.images || [])[0] || {} }));
      return h('div', { className: 'photo-preview' },
        h('style', {}, `
          body{margin:0!important;background:#fff!important;color:#0a0a0a!important}
          .photo-preview{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;background:#fff;color:#0a0a0a}
          .pp-header{display:flex;align-items:center;justify-content:space-between;padding:18px 20px;font-size:14px;position:sticky;top:0;background:#fff;z-index:2}
          .pp-header strong{letter-spacing:-.03em}.pp-header button,.pp-view{border:0;background:none;color:inherit;font:inherit;cursor:pointer;padding:8px}
          .pp-slide{height:calc(100vh - 64px);min-height:360px;display:flex;flex-direction:column;gap:16px;padding:8px 20px 18px;box-sizing:border-box}
          .pp-stage{display:flex;align-items:center;justify-content:center;flex:1;min-height:0;border:0;padding:0;background:#fff;width:100%;color:#555;cursor:pointer}
          .pp-stage img{width:100%;height:100%;object-fit:contain;display:block;margin:0}
          .pp-caption{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;font-size:13px;line-height:1.4;flex-shrink:0}
          .pp-caption small{display:block;font-size:12px;color:#555;margin-top:4px}.pp-caption>div{overflow-wrap:anywhere}
          .pp-view{white-space:nowrap;font-size:12px}.pp-empty{padding:32px;font-size:14px}
        `),
        h('header', { className: 'pp-header' }, h('strong', {}, 'MATT ADAM'),
          active ? h('button', { type: 'button', onClick: () => this.setState({ projectIndex: null }) }, 'Back ↗') : h('span', {}, data.contact_label || 'Contact')),
        !slides.length && h('p', { className: 'pp-empty' }, 'Add a project and photograph to see the preview.'),
        slides.map(({ project, photo, index }) => {
          const src = resolve(photo.image);
          const open = () => { if (!active) this.setState({ projectIndex: index }); };
          return h('section', { className: 'pp-slide', key: `${active ? 'image' : 'cover'}-${index}` },
            h(active ? 'div' : 'button', { className: 'pp-stage', type: active ? undefined : 'button', onClick: open, 'aria-label': project.title || 'Project' },
              src ? h('img', { src, alt: photo.alt || project.title || 'Photograph' }) : h('span', {}, 'Choose a photograph')),
            h('footer', { className: 'pp-caption' },
              h('div', {}, project.title || 'Untitled project', h('small', {}, active ? photo.caption || project.description : project.description)),
              active ? h('span', { className: 'pp-view' }, `${index + 1} / ${slides.length}`) : h('button', { className: 'pp-view', type: 'button', onClick: open }, 'View ↗')));
        }));
    }
  });
  window.CMS.registerPreviewTemplate('photography', PhotographyPreview);
})();
