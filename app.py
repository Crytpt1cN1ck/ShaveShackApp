# app.py — The Shave Shack Random Special (clean, centered, working)

import random
import streamlit as st

# ---------- MENU ----------
FLAVORS_BASE = [
    "Lemon-Lime", "Cherry", "Orange", "Bubble Gum", "Banana", "Blue Razzberry",
    "Tiger Blood", "Pink Lemonade", "Peach", "Grape", "Vanilla", "Pina Colada",
    "Cotton Candy", "Sour Apple", "Strawberry", "Root Beer", "Blackberry",
    "Watermelon", "Blueberry"
]
TOPPINGS_BASE = [
    "Gummy Sharks", "Nerds", "Sweet Cream", "Sour Patch Kids",
    "Popping Candy", "Whipped Cream", "Peach Rings", "Swedish Fish"
]

# Banana is not gluten-free; all others are GF.
FLAVOR_INFO = {f: {"gluten_free": (f != "Banana")} for f in FLAVORS_BASE}
TOPPING_INFO = {
    "Gummy Sharks":   {"dairy": False, "price": 0.50},
    "Nerds":          {"dairy": False, "price": 0.50},
    "Sweet Cream":    {"dairy": True,  "price": 0.50},
    "Sour Patch Kids":{"dairy": False, "price": 0.50},
    "Popping Candy":  {"dairy": False, "price": 1.00},
    "Whipped Cream":  {"dairy": True,  "price": 0.50},
    "Peach Rings":    {"dairy": False, "price": 0.50},
    "Swedish Fish":   {"dairy": False, "price": 0.50},
}

MAX_FLAVORS = 3
MAX_TOPPINGS = 2

# ---------- STATE ----------
def init_state():
    ss = st.session_state
    ss.setdefault("flavors", FLAVORS_BASE[:])
    ss.setdefault("toppings", TOPPINGS_BASE[:])
    ss.setdefault("removed_flavors", [])
    ss.setdefault("removed_toppings", [])
    ss.setdefault("chosen", {"flavs": [], "tops": []})
    ss.setdefault("gf_only", False)
    ss.setdefault("hide_dairy", False)
    # for Step 1 selectboxes
    ss.setdefault("flavor_select", None)
    ss.setdefault("topping_select", None)

init_state()

def reset_all():
    ss = st.session_state
    ss.flavors = FLAVORS_BASE[:]
    ss.toppings = TOPPINGS_BASE[:]
    ss.removed_flavors = []
    ss.removed_toppings = []
    ss.chosen = {"flavs": [], "tops": []}
    ss.gf_only = False
    ss.hide_dairy = False

    # ✅ safely clear widget-backed keys
    ss.pop("flavor_select", None)
    ss.pop("topping_select", None)
    ss.pop("want_flavs", None)
    ss.pop("want_tops", None)
    ss.pop("_flash", None)
    
import base64

def img_b64(path): 
    import base64, pathlib
    return base64.b64encode(pathlib.Path(path).read_bytes()).decode("utf-8")

def fmt_list(items):
    if not items: return "None"
    if len(items) == 1: return items[0]
    return f"{', '.join(items[:-1])}, and {items[-1]}"

def sample_unique(items, n):
    items = items[:]
    random.shuffle(items)
    return items[:min(n, len(items))]

def price_for_toppings(tops):
    return round(sum(TOPPING_INFO[t]["price"] for t in tops), 2)

# ---------- PAGE HEADER ----------
st.set_page_config(page_title="The Shave Shack – Random Special", page_icon="🦈", layout="centered")

def middle(width=8):
    """Return a centered column whose width is 'width' (surrounded by 1-1 spacers)."""
    return st.columns([1, width, 1])[1]

def CHEADING(text, level=2):
    st.markdown(f"<h{level} style='text-align:center'>{text}</h{level}>", unsafe_allow_html=True)
    
import streamlit.components.v1 as components

# If a previous action requested a scroll-to-top, do it now and clear the flag
if st.session_state.get("_scroll_to_top"):
    components.html(
        "<script>window.scrollTo({ top: 0, behavior: 'smooth' });</script>",
        height=0, width=0
    )
    st.session_state["_scroll_to_top"] = False

# Title
st.markdown("<h2 style='text-align:center'>====================================</h2>", unsafe_allow_html=True)
# Center the logo + title together as one block (no HTML <img> path issues)
logo_b64 = img_b64("logo.png")  # adjust path if needed

# Center the logo and title horizontally and vertically aligned
st.markdown(
    f"""
    <div style="
        display:flex;
        align-items:center;           /* vertical centering */
        justify-content:center;       /* center as one unit */
        flex-wrap:nowrap;             /* keep on one line */
        gap:16px;                     /* space between logo and text */
        margin:0 auto;
        max-width: 760px;             /* ↓ reduce total row width */
        width:100%;">
      <img src="data:image/png;base64,{logo_b64}"
           style="width:300px; height:auto; display:block;" />
      <div style="display:flex; align-items:center; justify-content:center; max-width: 420px;">
        <h1 style="margin:0; text-align:center; line-height:1.1;">
          Welcome to<br>The Shave Shack!
        </h1>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

#st.markdown("<h1 style='text-align:center'>Welcome to The Shave Shack!</h1>", #unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center'>====================================</h2>", unsafe_allow_html=True)

with middle():
    st.markdown("<h3 style='text-align:center'>Can't decide what you want to order?</h3>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center'>Let's build a random special made just for you, in 4 simple steps!</h3>", unsafe_allow_html=True)

# ---------- RULES / INFO ----------
with st.expander("Menu & Allergen/Price Info"):
    st.markdown("""
    <ul style="margin: 0 0 0 1rem;">
      <li><strong>Maximum of 3 flavors</strong> and <strong>maximum of 2 toppings.</strong></li>
      <li><strong>Banana</strong> is the only flavor <strong>not gluten-free;</strong> all other flavors are gluten-free.</li>
      <li>All flavors are free of <strong>peanuts, tree nuts, dairy, eggs, soy, wheat, fish, and shellfish.</strong></li>
      <li><strong>Whipped Cream</strong> and <strong>Sweet Cream</strong> contain dairy.</li>
      <li><strong>Toppings are $0.50 each, except Popping Candy which is $1.00.</strong></li>
    </ul>
    """, unsafe_allow_html=True)

    
def toggle_select_item(kind_label, select_key, pool_key, removed_key):
    """Toggle the currently selected item in `select_key` between pool and removed.
    Clears the selectbox afterwards."""
    sel = st.session_state.get(select_key)
    if not sel:
        st.session_state["_flash"] = f"Pick a {kind_label} first."
        return

    items   = st.session_state[pool_key]
    removed = st.session_state[removed_key]

    if sel in items:
        items.remove(sel)
        if sel not in removed:
            removed.append(sel)
        st.session_state["_flash"] = f"Removed {kind_label}: {sel}"
    elif sel in removed:
        removed.remove(sel)
        if sel not in items:
            items.append(sel)
        st.session_state["_flash"] = f"Added {kind_label} back: {sel}"
    else:
        st.session_state["_flash"] = f"{kind_label.capitalize()} '{sel}' not found."

    # Clear selection for the next render
    st.session_state[select_key] = None
st.divider()

# ---------- STEP 1: Remove / add back by name (select + button) ----------
CHEADING("1) Exclude flavors and/or toppings", level=2)
with middle():
    left, right = st.columns(2)

    # ----- Left: Flavors (search + toggle) -----
    with left:
        st.markdown(
            "<div style='text-align:center'><strong>Flavors</strong><br>"
            "<span style='opacity:0.8'>Pick a flavor, then tap</span></div>",
            unsafe_allow_html=True
        )

        all_flavors = sorted(set(st.session_state.flavors + st.session_state.removed_flavors))
        flavor_choice = st.selectbox(
            "Choose a flavor",
            options=all_flavors,
            index=all_flavors.index(st.session_state.flavor_select) if st.session_state.flavor_select in all_flavors else None,
            placeholder="Start typing to search…",
            key="flavor_select",
            label_visibility="collapsed",
        )

        # Decide button label from current selection
        in_current = (flavor_choice in st.session_state.flavors) if flavor_choice else False
        in_removed = (flavor_choice in st.session_state.removed_flavors) if flavor_choice else False
        flavor_btn_label = (
            "Remove Flavor" if in_current else
            "Add Flavor Back" if in_removed else
            "Apply Selection"
        )

        st.button(
            flavor_btn_label,
            use_container_width=True,
            key="flavor_toggle_btn",
            on_click=toggle_select_item,
            args=("flavor", "flavor_select", "flavors", "removed_flavors"),
        )

    # ----- Right: Toppings (search + toggle) -----
    with right:
        st.markdown(
            "<div style='text-align:center'><strong>Toppings</strong><br>"
            "<span style='opacity:0.8'>Pick a topping, then tap</span></div>",
            unsafe_allow_html=True
        )

        all_toppings = sorted(set(st.session_state.toppings + st.session_state.removed_toppings))
        topping_choice = st.selectbox(
            "Choose a topping",
            options=all_toppings,
            index=all_toppings.index(st.session_state.topping_select) if st.session_state.topping_select in all_toppings else None,
            placeholder="Start typing to search…",
            key="topping_select",
            label_visibility="collapsed",
        )

        in_current = (topping_choice in st.session_state.toppings) if topping_choice else False
        in_removed = (topping_choice in st.session_state.removed_toppings) if topping_choice else False
        topping_btn_label = (
            "Remove Topping" if in_current else
            "Add Topping Back" if in_removed else
            "Apply Selection"
        )

        st.button(
            topping_btn_label,
            use_container_width=True,
            key="topping_toggle_btn",
            on_click=toggle_select_item,
            args=("topping", "topping_select", "toppings", "removed_toppings"),
        )


# Optional: show removed items (open by default)
with middle():
    if st.session_state.removed_flavors or st.session_state.removed_toppings:
        with st.expander("Removed items (tap to restore)", expanded=True):
            cL, cR = st.columns(2)
            with cL:
                st.markdown("**Flavors**")
                for f in sorted(st.session_state.removed_flavors):
                    if st.button(f"Add back: {f}", key=f"restore_f_{f}"):
                        st.session_state.removed_flavors.remove(f)
                        if f not in st.session_state.flavors:
                            st.session_state.flavors.append(f)
                        st.rerun()
            with cR:
                st.markdown("**Toppings**")
                for t in sorted(st.session_state.removed_toppings):
                    if st.button(f"Add back: {t}", key=f"restore_t_{t}"):
                        st.session_state.removed_toppings.remove(t)
                        if t not in st.session_state.toppings:
                            st.session_state.toppings.append(t)
                        st.rerun()
                     
# optional quick status feedback
if "_flash" in st.session_state:
    st.info(st.session_state.pop("_flash"))
st.divider()

# ---------- STEP 2: Dietary filters (toggle buttons) ----------
CHEADING("2) Dietary filters (optional)", level=2)
with middle():
    c1, c2 = st.columns([1, 1])
    with c1:
        gf_label = "✅ Gluten-Free Only" if st.session_state.gf_only else "Gluten-Free Only"
        if st.button(gf_label, use_container_width=True, key="gf_toggle"):
            st.session_state.gf_only = not st.session_state.gf_only
            st.rerun()
    with c2:
        dairy_label = "🚫 No Dairy" if st.session_state.hide_dairy else "No Dairy"
        if st.button(dairy_label, use_container_width=True, key="dairy_toggle"):
            st.session_state.hide_dairy = not st.session_state.hide_dairy
            st.rerun()
    st.markdown(
        '<p style="text-align:center; font-size:0.9rem; opacity:0.8;">'
        'Tip: Tap again to turn a filter off.'
        '</p>',
        unsafe_allow_html=True
    )


# Filtered availability
avail_flavors = [f for f in st.session_state.flavors
                 if (FLAVOR_INFO[f]["gluten_free"] or not st.session_state.gf_only)]
avail_toppings = [t for t in st.session_state.toppings
                  if (not TOPPING_INFO[t]["dairy"] or not st.session_state.hide_dairy)]

with middle():
    st.write(f"**Available flavors now ({len(avail_flavors)}):** {', '.join(avail_flavors) or 'None'}")
    st.write(f"**Available toppings now ({len(avail_toppings)}):** {', '.join(avail_toppings) or 'None'}")
st.divider()

# ---------- STEP 3: How many (emoji + big ±) ----------
CHEADING("3) How many flavors and toppings?", level=2)

max_flavs = min(MAX_FLAVORS, len(avail_flavors))
max_tops  = min(MAX_TOPPINGS, len(avail_toppings))

if "want_flavs" not in st.session_state:
    st.session_state.want_flavs = 1 if max_flavs >= 1 else 0
if "want_tops" not in st.session_state:
    st.session_state.want_tops = 0
st.session_state.want_flavs = max(0, min(st.session_state.want_flavs, max_flavs))
st.session_state.want_tops  = max(0, min(st.session_state.want_tops,  max_tops))

def _inc_count(key, max_value):
    st.session_state[key] = min(max_value, st.session_state.get(key, 0) + 1)

def _dec_count(key):
    st.session_state[key] = max(0, st.session_state.get(key, 0) - 1)

def plus_minus_row(title, key, max_value, emoji):
    with middle():
        minus, label, plus = st.columns([1, 6, 1])

        with minus:
            st.button(
                "➖",
                key=f"dec_{key}",
                use_container_width=True,
                on_click=_dec_count,
                args=(key,),
            )

        with label:
            st.markdown(
                f"""
                <div style='text-align:center;'>
                  <span style="
                    display:inline-block;
                    padding:.35rem .85rem;
                    border-radius:999px;
                    background:linear-gradient(90deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
                    border:1px solid rgba(255,255,255,.12);
                    box-shadow:0 6px 18px rgba(0,0,0,.12) inset, 0 4px 14px rgba(0,0,0,.08);
                    font-size:1.25rem; font-weight:700;">
                    {emoji[0]}{emoji[1]} {title}: {st.session_state[key]} {emoji[2]}{emoji[3]}
                  </span>
                </div>
                """,
                unsafe_allow_html=True
)



        with plus:
            st.button(
                "➕",
                key=f"inc_{key}",
                use_container_width=True,
                on_click=_inc_count,
                args=(key, max_value),
            )


plus_minus_row("Flavors",  "want_flavs", max_flavs, ["🍓","🍒","🫐","🍌"])
plus_minus_row("Toppings", "want_tops",  max_tops,  ["🍭","🍬","🍫","🥛"])

want_flavs = st.session_state.want_flavs
want_tops  = st.session_state.want_tops
st.divider()

# ---------- STEP 4: Build / Sharky / Reset ----------
CHEADING("4) Build your Random Special", level=2)
with middle():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        build_clicked = st.button("Build My Special 🍧", use_container_width=True)
    with col2:
        sharky_clicked = st.button("I’m Feeling Sharky 🦈", use_container_width=True)
    def handle_start_over():
        reset_all()
        st.session_state["_scroll_to_top"] = True  # tell the next render to scroll

    with col3:
        st.button(
            "Start Over 🔄",
            use_container_width=True,
            key="start_over_btn",
            on_click=handle_start_over,
        )
    st.markdown(
        '<p style="text-align:center; font-size:0.9rem; opacity:0.8;">'
        'Tip: Want a surprise with toppings too? Try “I’m Feeling Sharky 🦈”.'
        '</p>',
        unsafe_allow_html=True
    )





if build_clicked:
    st.session_state.chosen["flavs"] = sample_unique(avail_flavors, want_flavs)
    st.session_state.chosen["tops"]  = sample_unique(avail_toppings, want_tops)
    st.balloons()   # 🎈
if sharky_clicked:
    # Require at least 2 flavors and 1 topping when possible
    if len(avail_flavors) < 2 or len(avail_toppings) < 1:
        st.warning("Not enough available items to build a Sharky combo (need ≥2 flavors and ≥1 topping).")
    else:
        f = min(len(avail_flavors), random.randint(2, 3))  # 2–3 flavors
        t = min(len(avail_toppings), random.randint(1, 2)) # 1–2 toppings
        st.session_state.chosen["flavs"] = sample_unique(avail_flavors, f)
        st.session_state.chosen["tops"]  = sample_unique(avail_toppings, t)
    st.balloons()   # 🎈
#if reset_clicked:
    #reset_all()
    #st.rerun()

chosen_flavs = st.session_state.chosen["flavs"]
chosen_tops  = st.session_state.chosen["tops"]

# ---------- RESULT & FOOTER ----------
if chosen_flavs or chosen_tops:
    st.markdown("---")
    with middle():
        st.markdown("<h3 style='text-align:center'>~~~ Here’s your random special ~~~</h3>", unsafe_allow_html=True)
        st.markdown(
            f"<h5 style='text-align:center; margin-top:0.5em;'>Your flavors are: "
            f"<span style='font-weight:600'>{fmt_list(chosen_flavs)}</span>.</h5>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<h5 style='text-align:center; margin-top:0.2em;'>Your toppings are: "
            f"<span style='font-weight:600'>{fmt_list(chosen_tops)}</span>.</h5>",
            unsafe_allow_html=True
        )

        if any(TOPPING_INFO[t]["dairy"] for t in chosen_tops):
            st.markdown(
                """
                <div style="
                    background-color:#fff3cd;
                    border:1px solid #ffeeba;
                    color:#856404;
                    padding:0.75rem 1rem;
                    border-radius:8px;
                    text-align:center;
                    font-weight:600;">
                    ⚠️ Contains dairy (Whipped Cream or Sweet Cream).
                </div>
                """,
                unsafe_allow_html=True
            )

        est = price_for_toppings(chosen_tops)
        # Pretty, stable pricing note (no markdown quirks)
        st.markdown(
            f"""
            <div style="
                background:#1f3b57; 
                color:#e6eef6;
                text-align: center;
                padding:0.9rem 1rem; 
                border-radius:12px; 
                margin:0.5rem 0 0.25rem 0;">
              Toppings are <strong>$0.50</strong> each, except <strong>Popping Candy</strong> which is <strong>$1.00</strong>.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Polished "Order details" (no raw JSON)
        with st.expander("Order details", expanded=True):
            est = price_for_toppings(chosen_tops)  # you already calculate this; reuse it
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; align-items:center; margin:.25rem 0 0.5rem 0;">
                  <strong style="font-size:1.05rem;">Added Toppings Cost</strong>
                  <span style="
                    padding:.25rem .6rem; border-radius:999px;
                    background:rgba(31,59,87,.9); color:#e6eef6; font-weight:700;">
                    ${est:.2f}
                  </span>
                </div>
                """,
                unsafe_allow_html=True
            )
            cL, cR = st.columns(2)
            with cL:
                st.markdown("**Flavors**")
                st.markdown("\n".join([f"- {f}" for f in chosen_flavs]) or "_None_")
            with cR:
                st.markdown("**Toppings**")
                st.markdown("\n".join([f"- {t}" for t in chosen_tops]) or "_None_")
            st.markdown("---")
            st.markdown(f"**Gluten-free filter:** {'On' if st.session_state.gf_only else 'Off'}")
            st.markdown(f"**No-dairy filter:** {'On' if st.session_state.hide_dairy else 'Off'}")

st.markdown('<hr class="ss-hr">', unsafe_allow_html=True)
with middle():
    st.markdown(
        "<h3 style='text-align:center; opacity:.9; font-weight:600;'>"
        "Thanks for playing — and thanks for visiting <em>The Shave Shack</em>! 🦈🍧"
        "</h3>",
        unsafe_allow_html=True
    )

