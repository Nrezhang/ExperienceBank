import { useEffect, useState } from "react";

async function request(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || "Something went wrong.");
  }
  return response.status === 204 ? null : response.json();
}

export default function App() {
  const [items, setItems] = useState([]);
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function loadItems() {
    try {
      const data = await request("/api/items");
      setItems(data.items);
    } catch (error) {
      setMessage(error.message);
    }
  }

  useEffect(() => {
    loadItems();
  }, []);

  async function createItem(event) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      await request("/api/items", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ title }),
      });
      setTitle("");
      await loadItems();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  async function deleteItem(item) {
    setBusy(true);
    setMessage("");
    try {
      await request(`/api/items/${encodeURIComponent(item.id)}`, { method: "DELETE" });
      await loadItems();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <p className="eyebrow">AWS FULL-STACK STARTER</p>
      <h1>Keep the ideas worth returning to.</h1>
      <p className="intro">A tiny idea bank backed by Python and DynamoDB.</p>

      <form onSubmit={createItem}>
        <label htmlFor="title">New idea</label>
        <div className="form-row">
          <input
            id="title"
            name="title"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            maxLength={120}
            placeholder="Write something memorable…"
            required
          />
          <button type="submit" disabled={busy}>Save idea</button>
        </div>
        <p className="message" role="status" aria-live="polite">{message}</p>
      </form>

      <section aria-labelledby="ideas-heading">
        <div className="section-heading">
          <h2 id="ideas-heading">Your ideas</h2>
          <span>{items.length}</span>
        </div>
        <ul>
          {items.map((item) => (
            <li key={item.id}>
              <span>{item.title}</span>
              <button
                type="button"
                disabled={busy}
                aria-label={`Delete ${item.title}`}
                onClick={() => deleteItem(item)}
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
        {items.length === 0 && <p className="empty">No ideas yet. Add the first one above.</p>}
      </section>
    </main>
  );
}
