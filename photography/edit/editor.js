"use strict";
const REPO = "Mattadam3000/portfolio",
  OWNER = 164549058,
  AUTH = "https://sveltia-cms-auth.mattadamco.workers.dev";
const $ = (s) => document.querySelector(s),
  clone = (x) => structuredClone(x),
  esc = (s) =>
    String(s ?? "").replace(
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
let token = "",
  data,
  baseSha,
  selected = null,
  assets = {},
  urls = {},
  history = [],
  busy = false,
  db,
  saveQueue = Promise.resolve(),
  dragIndex = null,
  pollTimer,
  publishedData,
  publicTemplate = "",
  saveTimer = null,
  saving = false,
  uploaded = {};
const status = (s) => ($("#status").textContent = s);
async function api(path, method = "GET", body) {
  const r = await fetch("https://api.github.com" + path, {
    method,
    headers: {
      Authorization: "Bearer " + token,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  if (!r.ok) {
    const e = new Error(
      r.status === 401
        ? "Your session expired. Sign in again."
        : `GitHub ${r.status}: ${(await r.json()).message || "Request failed"}`,
    );
    e.status = r.status;
    throw e;
  }
  return r.status === 204 ? null : r.json();
}
const repo = (path, method, body) => api("/repos/" + REPO + path, method, body);
function database() {
  return new Promise((resolve, reject) => {
    const r = indexedDB.open("mattadam-photography-studio", 1);
    r.onupgradeneeded = () => r.result.createObjectStore("draft");
    r.onsuccess = () => resolve(r.result);
    r.onerror = () => reject(r.error);
  });
}
function readDraft() {
  return new Promise((resolve, reject) => {
    const r = db.transaction("draft").objectStore("draft").get("owner");
    r.onsuccess = () => resolve(r.result);
    r.onerror = () => reject(r.error);
  });
}
function save() {
  clearTimeout(saveTimer);
  saveTimer = null;
  saving = true;
  const snapshot = {
    data: clone(data),
    baseSha,
    assets: clone(assets),
    uploaded: clone(uploaded),
  };
  status("Saving private draft…");
  saveQueue = saveQueue
    .catch(() => {})
    .then(
      () =>
        new Promise((resolve, reject) => {
          const tx = db.transaction("draft", "readwrite");
          tx.objectStore("draft").put(snapshot, "owner");
          tx.oncomplete = () => resolve();
          tx.onerror = () => reject(tx.error);
          tx.onabort = () => reject(tx.error);
        }),
    );
  saveQueue.then(
    () => {
      saving = false;
      if (!busy) status("Draft saved on this device · not published");
    },
    () => {
      saving = false;
      status("Draft could not be saved. Keep this tab open.");
    },
  );
  return saveQueue;
}
function checkpoint() {
  history.push(clone(data));
  if (history.length > 40) history.shift();
}
function changed() {
  clearTimeout(saveTimer);
  status("Saving private draft…");
  saveTimer = setTimeout(save, 350);
  $("#undo").disabled = !history.length;
}
function src(path) {
  if (assets[path])
    return urls[path] || (urls[path] = URL.createObjectURL(assets[path]));
  return path && /^(https:\/\/|\/img\/)/.test(path) ? path : "";
}
function current() {
  return data.projects.find((p) => p.slug === selected);
}
function field(tag, value, label, handler) {
  const el = document.createElement(tag);
  el.value = value || "";
  el.placeholder = label;
  el.setAttribute("aria-label", label);
  el.addEventListener("focus", checkpoint);
  el.addEventListener("input", () => {
    handler(el.value);
    changed();
  });
  return el;
}
function button(label, handler, cls = "") {
  const b = document.createElement("button");
  b.textContent = label;
  b.className = cls;
  b.onclick = handler;
  return b;
}
function move(list, from, to) {
  if (busy || to < 0 || to >= list.length || from === to) return;
  checkpoint();
  list.splice(to, 0, list.splice(from, 1)[0]);
  changed();
  render();
}
function render() {
  const p = current();
  $("#heading").textContent = p ? "Edit project" : "Your work";
  $("#back").hidden = !p;
  $("#add").hidden = !!p;
  $("#undo").disabled = !history.length;
  const ws = $("#workspace");
  ws.replaceChildren();
  if (p) {
    const details = document.createElement("div");
    details.className = "project-details";
    details.append(
      field("input", p.title, "Project title", (v) => (p.title = v)),
      field(
        "textarea",
        p.description,
        "Project description",
        (v) => (p.description = v),
      ),
    );
    ws.append(details);
    const drop = document.createElement("div");
    drop.className = "dropzone";
    drop.tabIndex = 0;
    drop.setAttribute("role", "button");
    drop.textContent = "+ Drop photographs here, or click to upload";
    drop.onclick = () => $("#files").click();
    drop.onkeydown = (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        $("#files").click();
      }
    };
    drop.ondragover = (e) => {
      e.preventDefault();
      drop.classList.add("over");
    };
    drop.ondragleave = () => drop.classList.remove("over");
    drop.ondrop = (e) => {
      e.preventDefault();
      drop.classList.remove("over");
      upload(e.dataTransfer.files);
    };
    ws.append(drop);
  }
  const list = p ? p.images : data.projects,
    grid = document.createElement("div");
  grid.className = "grid";
  ws.append(grid);
  if (!list.length) {
    const e = document.createElement("p");
    e.className = "empty";
    e.textContent = p
      ? "Add the first photographs for this project."
      : "Add a project to start arranging your work.";
    ws.append(e);
  }
  list.forEach((item, i) => {
    const card = document.createElement("article");
    card.className = "card" + (!p && item.published === false ? " muted" : "");
    const pic = document.createElement(p ? "div" : "button");
    pic.className = "image-box";
    const path = p ? item.image : item.cover || item.images[0]?.image;
    if (path) {
      const img = document.createElement("img");
      img.src = src(path);
      img.alt = p ? item.alt || p.title : item.title;
      img.loading = "lazy";
      pic.append(img);
    } else pic.textContent = "Add photographs";
    if (!p) {
      pic.setAttribute("aria-label", "Open " + item.title);
      pic.onclick = () => {
        selected = item.slug;
        render();
        window.scrollTo(0, 0);
      };
    }
    card.append(pic);
    if (!p)
      card.append(
        field("input", item.title, "Project title", (v) => (item.title = v)),
        field(
          "textarea",
          item.description,
          "Project description",
          (v) => (item.description = v),
        ),
      );
    else
      card.append(
        field(
          "textarea",
          item.caption,
          "Caption (optional)",
          (v) => (item.caption = v),
        ),
        field(
          "input",
          item.alt,
          "Image description / alt text",
          (v) => (item.alt = v),
        ),
      );
    const actions = document.createElement("div");
    actions.className = "actions";
    const handle = button("↕ Drag", () => {}, "drag");
    handle.draggable = true;
    handle.setAttribute("aria-label", "Drag to reorder");
    handle.ondragstart = (e) => {
      dragIndex = i;
      e.dataTransfer.setData("text/plain", String(i));
      e.dataTransfer.effectAllowed = "move";
    };
    handle.ondragend = () => {
      dragIndex = null;
      document
        .querySelectorAll(".over")
        .forEach((e) => e.classList.remove("over"));
    };
    card.ondragover = (e) => {
      if (dragIndex !== null) {
        e.preventDefault();
        card.classList.add("over");
      }
    };
    card.ondragleave = () => card.classList.remove("over");
    card.ondrop = (e) => {
      if (dragIndex === null) return;
      e.preventDefault();
      move(list, dragIndex, i);
      dragIndex = null;
    };
    actions.append(
      handle,
      button("←", () => move(list, i, i - 1)),
      button("→", () => move(list, i, i + 1)),
    );
    if (p) {
      const isCover = (p.cover || p.images[0]?.image) === item.image;
      actions.append(
        button(isCover ? "● Cover" : "Set cover", () => {
          checkpoint();
          p.cover = item.image;
          changed();
          render();
        }),
      );
    } else
      actions.append(
        button(item.published === false ? "Hidden" : "Visible", () => {
          checkpoint();
          item.published = item.published === false;
          changed();
          render();
        }),
      );
    actions.append(
      button(
        "Remove",
        () => {
          checkpoint();
          list.splice(i, 1);
          if (p && p.cover === item.image) p.cover = "";
          changed();
          render();
        },
        "remove",
      ),
    );
    card.append(actions);
    grid.append(card);
  });
}
async function upload(files) {
  files = Array.from(files);
  if (busy || !current()) return;
  const p = current();
  setBusy(true);
  checkpoint();
  const errors = [];
  for (const file of files) {
    try {
      if (!["image/jpeg", "image/png", "image/webp"].includes(file.type))
        throw Error("Use JPG, PNG, or WebP");
      status("Preparing " + file.name + "…");
      const bitmap = await createImageBitmap(file, {
        imageOrientation: "from-image",
      });
      const scale = Math.min(1, 2800 / Math.max(bitmap.width, bitmap.height)),
        canvas = document.createElement("canvas");
      canvas.width = Math.round(bitmap.width * scale);
      canvas.height = Math.round(bitmap.height * scale);
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "#fff";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
      bitmap.close();
      const blob = await new Promise((r) =>
        canvas.toBlob(r, "image/jpeg", 0.92),
      );
      if (!blob) throw Error("Could not prepare image");
      const path = "/img/photography/" + crypto.randomUUID() + ".jpg";
      assets[path] = blob;
      p.images.push({ image: path, alt: "", caption: "" });
      render();
      await save();
    } catch (e) {
      errors.push(file.name + ": " + e.message);
    }
  }
  setBusy(false);
  changed();
  if (errors.length) alert(errors.join("\n"));
}
function setBusy(value) {
  busy = value;
  $("#workspace").inert = value;
  document
    .querySelectorAll("header button,.toolbar button")
    .forEach((b) => (b.disabled = value));
  if (!value) $("#undo").disabled = !history.length;
}
// A fresh frame avoids hidden-dialog scroll restoration and stale scroll-snap layout.
// Always render the current in-memory draft, including unpublished object URLs.
function preview(projectSlug = selected) {
  const p = data.projects.find(project => project.slug === projectSlug);
  const projects = p ? [p] : data.projects.filter(project => project.published !== false);
  const slides = projects.flatMap(project => (p ? project.images : [{image: project.cover || project.images[0]?.image}]).map((photo, i) => {
    const path = src(photo.image);
    const image = path ? `<img src="${esc(new URL(path, location.origin).href)}" alt="${esc(photo.alt || project.title)}" decoding="async">` : '<span>Add a photograph</span>';
    const stage = p ? `<div class="image-stage">${image}</div>` : `<a class="image-stage" href="#" data-preview-project="${esc(project.slug)}">${image}</a>`;
    return `<section class="slide">${stage}<footer class="caption"><div class="project-label"><span>${esc(project.title)}</span><span class="description">${esc(photo.caption || project.description)}</span></div>${p ? '' : `<a class="view-link" href="#" data-preview-project="${esc(project.slug)}">View ↗</a>`}</footer></section>`;
  })).join('');
  const values = { MODE:p ? 'gallery' : 'portfolio', TITLE:'Private preview · Matt Adam', DESCRIPTION:'Private preview', CANONICAL:'', SLIDES:slides || '<section class="slide empty">No photographs yet.</section>', BACK:p ? '<a href="#" data-preview-back>Back ↗</a>' : '', CONTACT_URL:'#', CONTACT_LABEL:esc(data.contact_label || 'Contact') };
  const bridge = `<script>document.addEventListener('click', e => { const link=e.target.closest('a'); if(!link)return; e.preventDefault(); if(link.hasAttribute('data-preview-project'))parent.postMessage({type:'photography-preview-project',slug:link.dataset.previewProject},'*'); if(link.hasAttribute('data-preview-back'))parent.postMessage({type:'photography-preview-back'},'*'); });<\/script>`;
  const oldFrame = $('#preview-frame');
  const frame = document.createElement('iframe');
  frame.id = 'preview-frame'; frame.title = 'Photography preview';
  frame.setAttribute('sandbox', 'allow-scripts');
  frame.className = oldFrame.className;
  const viewer = $('#viewer');
  if (!viewer.open) viewer.showModal();
  oldFrame.replaceWith(frame);
  frame.srcdoc = publicTemplate.replace(/{{(\w+)}}/g, (_, key) => values[key] || '').replace('</body>', bridge + '</body>');
}
window.addEventListener('message', event => {
  if (!$('#viewer').open || event.source !== $('#preview-frame').contentWindow) return;
  if (event.data?.type === 'photography-preview-back') preview(null);
  if (event.data?.type === 'photography-preview-project' && data.projects.some(p => p.slug === event.data.slug)) preview(event.data.slug);
});
function validate() {
  const slugs = new Set();
  for (const p of data.projects) {
    if (
      !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(p.slug) ||
      p.slug === "edit" ||
      slugs.has(p.slug)
    )
      throw Error("Project URLs must be unique.");
    slugs.add(p.slug);
    if (p.published !== false && (!p.title.trim() || !p.images.length))
      throw Error(
        "Add a title and photograph to every visible project, or hide it.",
      );
    for (const path of [...p.images.map((x) => x.image), p.cover].filter(
      Boolean,
    ))
      if (!/^(\/img\/|https:\/\/)/.test(path))
        throw Error("An image has an invalid address.");
  }
}
async function publish() {
  if (busy) return;
  try {
    validate();
    setBusy(true);
    await save();
    status("Checking published version…");
    let ref = await repo("/git/ref/heads/main"),
      head = ref.object.sha;
    const remote = await repo("/contents/photography.json?ref=" + head);
    if (remote.sha !== baseSha)
      throw Error(
        "Photography was changed elsewhere. Your draft is safe. Reset to published to load that version before editing again.",
      );
    const used = new Set(
      data.projects
        .flatMap((p) => [p.cover, ...p.images.map((x) => x.image)])
        .filter(Boolean),
    );
    const entries = [];
    for (const path of used) {
      if (!assets[path]) continue;
      if (uploaded[path]) {
        entries.push({
          path: path.slice(1),
          mode: "100644",
          type: "blob",
          sha: uploaded[path],
        });
        continue;
      }
      status(`Uploading photograph ${entries.length + 1}…`);
      const bytes = new Uint8Array(await assets[path].arrayBuffer());
      let binary = "";
      for (let i = 0; i < bytes.length; i += 32768)
        binary += String.fromCharCode(...bytes.subarray(i, i + 32768));
      const blob = await repo("/git/blobs", "POST", {
        content: btoa(binary),
        encoding: "base64",
      });
      uploaded[path] = blob.sha;
      entries.push({
        path: path.slice(1),
        mode: "100644",
        type: "blob",
        sha: blob.sha,
      });
    }
    const contentBlob = await repo("/git/blobs", "POST", {
      content: JSON.stringify(data, null, 2) + "\n",
      encoding: "utf-8",
    });
    entries.push({
      path: "photography.json",
      mode: "100644",
      type: "blob",
      sha: contentBlob.sha,
    });
    let published;
    for (let attempt = 0; attempt < 3; attempt++) {
      ref = await repo("/git/ref/heads/main");
      head = ref.object.sha;
      const check = await repo("/contents/photography.json?ref=" + head);
      if (check.sha !== baseSha)
        throw Error(
          "Photography changed during publishing. Your private draft is preserved.",
        );
      const commit = await repo("/git/commits/" + head),
        tree = await repo("/git/trees", "POST", {
          base_tree: commit.tree.sha,
          tree: entries,
        }),
        next = await repo("/git/commits", "POST", {
          message: "Update photography from visual studio",
          tree: tree.sha,
          parents: [head],
        });
      try {
        await repo("/git/refs/heads/main", "PATCH", {
          sha: next.sha,
          force: false,
        });
        published = next.sha;
        break;
      } catch (e) {
        if (![409, 422].includes(e.status) || attempt === 2) throw e;
      }
    }
    baseSha = contentBlob.sha;
    publishedData = JSON.stringify(data);
    history = [];
    await save();
    setBusy(false);
    status("Saved to GitHub · public site is building…");
    watchPublish(published);
    render();
  } catch (e) {
    setBusy(false);
    status(e.message);
  }
}
async function watchPublish(sha, attempt = 0) {
  clearTimeout(pollTimer);
  if (!token) return;
  try {
    const runs = await repo("/actions/runs?head_sha=" + sha + "&per_page=20"),
      run = runs.workflow_runs.find(
        (r) => r.path === ".github/workflows/build.yml",
      );
    if (run?.status === "completed") {
      status(
        run.conclusion === "success"
          ? (JSON.stringify(data) === publishedData ? "Published · public site updated" : "Last publish complete · newer draft is private")
          : "Saved to GitHub, but publishing failed. Check GitHub Actions.",
      );
      return;
    }
  } catch (e) {
    status("Saved to GitHub. Check the public site in a few minutes.");
    return;
  }
  if (attempt < 60)
    pollTimer = setTimeout(() => watchPublish(sha, attempt + 1), 5000);
  else
    status(
      "Saved to GitHub. Publishing is taking longer; check GitHub Actions.",
    );
}
async function start() {
  const user = await api("/user");
  if (user.id !== OWNER)
    throw Error("This studio is private to Matt’s GitHub account.");
  const permissions = await repo("");
  if (!permissions.permissions?.push)
    throw Error("This account does not have publishing access.");
  publicTemplate = await fetch("/photography-template.html", {cache:"no-store"}).then((r) => {
    if (!r.ok) throw Error("Could not load the page preview.");
    return r.text();
  });
  db = await database();
  const remote = await repo("/contents/photography.json?ref=main");
  const live = JSON.parse(
    new TextDecoder().decode(
      Uint8Array.from(atob(remote.content.replace(/\s/g, "")), (c) =>
        c.charCodeAt(0),
      ),
    ),
  );
  const draft = await readDraft();
  data = draft?.data || live;
  baseSha = draft?.baseSha || remote.sha;
  assets = draft?.assets || {};
  uploaded = draft?.uploaded || {};
  $("#login").hidden = true;
  $("#app").hidden = false;
  render();
  status(
    draft
      ? remote.sha !== baseSha
        ? "Draft restored · published content has changed elsewhere"
        : "Private draft restored on this device"
      : "Ready · changes stay private",
  );
}
$("#signin").onclick = () => {
  const popup = window.open(
    AUTH +
      "/auth?provider=github&site_id=" +
      encodeURIComponent(location.hostname) +
      "&scope=public_repo,read:user",
    "photography-login",
    "width=600,height=720",
  );
  if (!popup) {
    $("#login-status").textContent = "Allow the sign-in popup, then try again.";
    return;
  }
  $("#signin").disabled = true;
  $("#login-status").textContent = "Complete sign-in in the popup.";
  let timer;
  const cleanup = () => {
    window.removeEventListener("message", receive);
    clearInterval(timer);
    $("#signin").disabled = false;
  };
  const receive = async (event) => {
    if (
      event.origin !== AUTH ||
      event.source !== popup ||
      typeof event.data !== "string"
    )
      return;
    if (event.data === "authorizing:github") {
      popup.postMessage("authorizing:github", AUTH);
      return;
    }
    const match = event.data.match(
      /^authorization:github:(success|error):(.*)$/,
    );
    if (!match) return;
    cleanup();
    popup.close();
    try {
      const result = JSON.parse(match[2]);
      if (match[1] !== "success" || !result.token)
        throw Error("Sign-in was not completed.");
      token = result.token;
      await start();
    } catch (e) {
      token = "";
      $("#login-status").textContent = e.message;
    }
  };
  window.addEventListener("message", receive);
  timer = setInterval(() => {
    if (popup.closed) {
      cleanup();
      $("#login-status").textContent = "Sign-in window closed. Try again.";
    }
  }, 1000);
};
$("#logout").onclick = async () => {
  try {
    await save();
  } catch (e) {
    status("Could not save draft. Keep this tab open.");
    return;
  }
  token = "";
  clearTimeout(pollTimer);
  location.reload();
};
$("#back").onclick = () => {
  selected = null;
  render();
};
$("#add").onclick = () => {
  checkpoint();
  const slug = "project-" + crypto.randomUUID().slice(0, 8);
  data.projects.push({
    slug,
    title: "Untitled project",
    description: "",
    published: true,
    cover: "",
    images: [],
  });
  selected = slug;
  changed();
  render();
};
$("#files").onchange = (e) => {
  upload(e.target.files);
  e.target.value = "";
};
$("#undo").onclick = () => {
  if (history.length) {
    data = history.pop();
    if (!current()) selected = null;
    changed();
    render();
  }
};
$("#preview").onclick = () => preview();
$("#close-preview").onclick = () => $("#viewer").close();
$("#device").onclick = () => {
  const mobile = $("#preview-frame").classList.toggle("mobile");
  $("#device").textContent = mobile ? "Desktop view" : "Mobile view";
};
$("#publish").onclick = publish;
$("#discard").onclick = async () => {
  if (
    !confirm(
      "Replace this device’s private draft with the currently published work? Unpublished changes will be removed.",
    )
  )
    return;
  setBusy(true);
  try {
    const remote = await repo("/contents/photography.json?ref=main");
    data = JSON.parse(
      new TextDecoder().decode(
        Uint8Array.from(atob(remote.content.replace(/\s/g, "")), (c) =>
          c.charCodeAt(0),
        ),
      ),
    );
    baseSha = remote.sha;
    Object.values(urls).forEach(URL.revokeObjectURL);
    urls = {};
    assets = {};
    uploaded = {};
    history = [];
    selected = null;
    await save();
    render();
  } catch (e) {
    status(e.message);
  } finally {
    setBusy(false);
  }
};
window.addEventListener("beforeunload", (e) => {
  if (busy || saving || saveTimer) {
    e.preventDefault();
    e.returnValue = "";
  }
});
