import { useState } from "react";
import { useParams } from "react-router-dom";

function Payment() {
  const { bookingId } = useParams;
  const [error, setError] = useState(null);

  async function book() {
    try {
      const accessToken = sessionStorage.getItem("accessToken");

      const res = await fetch(
        "https://homely-mia-hng-c4ac2199.koyeb.app/booking/payment",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },

          body: JSON.stringify({
            booking_id: bookingId,
          }),
        }
      );
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
