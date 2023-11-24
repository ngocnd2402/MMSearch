const resultContainer = document.getElementById("result-container"),
    modal = document.getElementById("modal"),
    modalImage = document.getElementById("modal-image"),
    modalThumbnails = document.getElementById("modal-thumbnails"),
    ytbLink = document.getElementById("ytb"),
    objSubmit = document.getElementById("obj-submit"),
    captionContainer = document.getElementById("caption-container"),
    cart = document.getElementById("cart"),
    submit = document.getElementById("submit"),
    imageSearchModal = document.getElementById("image-search-modal"),
    imageSearchInput = document.getElementById("image-search-input"),
    methodElements = [document.getElementById("blip"), document.getElementById("slip"), document.getElementById("clip"), document.getElementById("ocr"), document.getElementById("asr")];
let currentImage = "",
    idx = "",
    resultData = [],
    topk = document.getElementById("topk").value,
    selectedFrame = "";
async function query() {
    let e = ["blip", "slip", "clip", "ocr", "asr"].filter((e) => document.getElementById(e).value);
    if (0 === e.length) {
        alert("No query entered");
        return;
    }
    let t = e.map((e) => document.getElementById(e).value);
    if (((topk = document.getElementById("topk").value), 1 === e.length)) {
        let a = new FormData();
        a.append("query", t[0]), a.append("topk", topk);
        try {
            let n = await fetch(`/${e[0]}_search`, { method: "POST", body: a });
            if (!n.ok) throw Error(`Failed to fetch results from the ${e[0]} API.`);
            (resultData = await n.json()), updateResults(resultData);
        } catch (l) {
            console.error(l);
        }
    } else {
        let r = { query: t, methods: e, topk: parseInt(topk) };
        try {
            let i = await fetch("/combine_search", { method: "POST", body: JSON.stringify(r), headers: { "Content-Type": "application/json" } });
            if (!i.ok) throw Error("Failed to fetch combined results from the API.");
            (resultData = await i.json()), updateResults(resultData);
        } catch (o) {
            console.error(o);
        }
    }
}
async function rightClick(e) {
    resultData = [];
    let t = new FormData();
    t.append("image_path", e), t.append("topk", topk);
    try {
        let a = await fetch("/image_search", { method: "POST", body: t });
        if (!a.ok) throw Error("Failed to fetch image results from the API.");
        resultData = await a.json();
    } catch (n) {
        console.error(n);
    }
    return resultData;
}
async function updateResults(e) {
    try {
        for (let t of ((resultContainer.innerHTML = ""), (resultData = e), (resultContainer.innerHTML = ""), e)) {
            let a = document.createElement("img"),
                n = t.frame,
                l = parseInt(n.split("/")[2], 10),
                r = n.split("/")[1],
                i = "/Frontend/Metadata/" + r + ".json",
                o = "/Frontend/Mapframe/" + r + ".csv";
            (a.src = "/Frontend/Reframe/" + n),
                a.classList.add("gallery_image", "hover_shadow", "cursor"),
                a.setAttribute("decoding", "async"),
                a.addEventListener("click", async () => {
                    try {
                        let e = await fetch(o);
                        if (e.ok) {
                            let t = await getPtsTime(await e.text(), l);
                            try {
                                let a = await fetch(i);
                                if (a.ok) {
                                    let r = await a.json();
                                    ytbLink.href = `${r.watch_url}&t=${t}s`;
                                } else console.error(a.status);
                            } catch (s) {
                                console.error(s);
                            }
                        }
                    } catch (d) {
                        console.log(d);
                    }
                    (currentImage = n), openGallery(n);
                }),
                a.addEventListener("contextmenu", async function (e) {
                    e.preventDefault();
                    try {
                        let t = await rightClick(`Frontend/Reframe/${n}`);
                        updateResults(t);
                    } catch (a) {
                        console.error(a);
                    }
                }),
                resultContainer.appendChild(a),
                modal.addEventListener("click", clickOutside);
        }
    } catch (s) {
        console.log(s);
    }
}
async function getPtsTime(e, t) {
    let a = e.split("\n");
    for (let n = 1; n < a.length; n++) {
        let l = a[n].split(","),
            r = parseInt(l[3]),
            i = parseFloat(l[1]);
        if (r === t) return i;
    }
    return null;
}
function getIndex(e, t) {
    let a = e.split("\n");
    for (let n = 1; n < a.length; n++) {
        let l = a[n].split(","),
            r = parseInt(l[3]),
            i = parseInt(l[0]);
        if (r == t) return i;
    }
    return null;
}
function getFrameID(e, t) {
    let a = e.split("\n");
    for (let n = 1; n < a.length; n++) {
        let l = a[n].split(","),
            r = parseInt(l[0]),
            i = parseInt(l[3]);
        if (r == t) return i;
    }
}
async function showFrameName(e) {
    let t = e.split("/")[1],
        a = parseInt(e.split("/")[2], 10);
    captionContainer.innerHTML = "";
    let n = document.createElement("p");
    n.classList.add("caption"), (n.innerHTML = t + ", " + a), captionContainer.appendChild(n);
}
async function openGallery(e) {
    modalThumbnails.innerHTML = "";
    let t = document.createDocumentFragment();
    for (let a = -3; a <= 3; a++) {
        let n = await getNextImage(e, a),
            l = document.createElement("img");
        (l.src = `/Frontend/Reframe/${n}`),
            l.classList.add("thumbnail"),
            l.addEventListener("error", () => {
                l.style.display = "none";
            }),
            l.addEventListener("click", () => {
                openGallery(n);
            }),
            t.appendChild(l);
    }
    modalThumbnails.appendChild(t), await openModal(e), modal.addEventListener("click", clickOutside);
}
async function openModal(e) {
    (modal.style.display = "flex"),
        (modal.style.alignItems = "center"),
        showSlides(e),
        modalThumbnails.querySelectorAll(".thumbnail").forEach((t) => {
            t.src.includes(e) ? t.classList.add("active") : t.classList.remove("active");
        });
}
function showSlides(e) {
    (modalImage.innerHTML = `<img src="/Frontend/Reframe/${e}" class="slides" id="slide">`),
        (currentImage = e),
        showFrameName(e),
        document.getElementById("slide").addEventListener("contextmenu", async function (t) {
            t.preventDefault(), closeModal(), updateResults(await rightClick(`Frontend/Reframe/${e}`));
        });
}
async function plusSlides(e) {
    let t = await getNextImage(currentImage, e),
        a = new Image();
    (a.src = `/Frontend/Reframe/${t}`),
        (a.onload = function () {
            openGallery(t);
        }),
        (a.onerror = function () {});
}
async function getNextImage(e, t) {
    let a = e.split("/"),
        n = parseInt(e.split("/")[2]),
        l = "/Frontend/Mapframe/" + a[1] + ".csv",
        r = "/Frontend/Metadata/" + a[1] + ".json";
    try {
        let i = await fetch(l);
        if (i.ok) {
            let o = (await i.text()).split("\n"),
                s = [];
            for (let d = 1; d < o.length; d++) {
                let [c, m, u, p] = o[d].split(",");
                s.push({ n: parseInt(c), pts_time: parseFloat(m), frame_idx: parseInt(p) });
            }
            let y = s.findIndex((e) => e.frame_idx === n);
            for (y += t; y >= s.length; ) y -= s.length;
            for (; y < 0; ) y += s.length;
            try {
                let g = await fetch(r),
                    h = s[y].pts_time;
                if (g.ok) {
                    let f = await g.json();
                    ytbLink.href = `${f.watch_url}&t=${h}s`;
                } else console.error(g.status);
            } catch (I) {
                console.error(I);
            }
            return `${a[0]}/${a[1]}/${(frame = s[y].frame_idx).toString().padStart(6, "0")}.jpg`;
        }
    } catch (E) {
        console.error(E);
    }
}
function closeModal() {
    modal.style.display = "none";
}
function clickOutside(e) {
    e.target === modal && closeModal();
}
function openImageSearch() {
    imageSearchModal.style.display = "flex";
}
async function searchImage() {
    let e = [];
    updateResults((e = await rightClick(imageSearchInput.value))), (imageSearchInput.value = ""), (imageSearchModal.style.display = "none");
}
function showNoti(e, t) {
    let a = document.getElementById("modal__noti");
    (a.textContent = e),
        (a.style.display = "block"),
        t ? (a.style.backgroundColor = "#4CAF50") : (a.style.backgroundColor = "#CE2029"),
        setTimeout(() => {
            a.style.display = "none";
        }, 1e3);
}
async function submitAnswer(e) {
    let t = e.split("/")[1],
        a = parseInt(e.split("/")[2], 10),
        n = "node01uyvv5h7d6xvv15o628610ok3w73",
        l = `https://eventretrieval.one/api/v1/submit?item=${t}&frame=${a}&session=${n}`;
    try {
        let r = await fetch(l, { method: "GET", headers: { Authorization: `Bearer ${n}` } });
        r.ok ? (showNoti("Success! Result submitted.", 1), (r.json().then((data) => {console.log(data)}))) : (showNoti("Error submitting the result.", 0), (r.json().then((data) => {console.log(data)})));
    } catch (i) {
        console.error("An error occurred:", i);
    }
}
submit.addEventListener("click", async () => {
    await submitAnswer(currentImage);
}),
    document.getElementById("topk"),
    methodElements.forEach((e) => {
        e.addEventListener("keypress", async function (e) {
            "Enter" === e.key && (e.preventDefault(), await query());
        });
    }),
    document.addEventListener("keydown", function (e) {
        "flex" === modal.style.display && ("ArrowLeft" === e.key ? plusSlides(-1) : "ArrowRight" === e.key && plusSlides(1));
    }),
    (window.onclick = function (e) {
        e.target === imageSearchModal && (imageSearchModal.style.display = "none");
    }),
    document.getElementById("image-search").addEventListener("click", searchImage),
    imageSearchInput.addEventListener("keypress", function (e) {
        "Enter" === e.key && searchImage();
    });
