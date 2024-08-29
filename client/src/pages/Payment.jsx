import { useState } from "react";

function Payment() {
  const [error, setError] = useState(null);

  async function book() {
    try {
      const res = await fetch("/api/payment");
      const data = await res.json();

      console.log(data);
    } catch (error) {
      setError(error.message);
    }
  }

  return (
    <main>
      <button onClick={book}>Pay me</button>
      {error && <p>Error: {error}</p>}
    </main>
  );
}

export default Payment;
