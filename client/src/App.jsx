import { BrowserRouter, Routes } from "react-router-dom";

import Homepage from "./pages/Homepage";
import MovieDetails from "./pages/MovieDetails";
import { Route } from "react-router-dom";
import Theater from "./pages/Theater";
import Signup from "./pages/Signup";
import Signin from "./pages/Signin";
import Booking from "./pages/Booking";
import ProtectRoute from "./components/ProtectRoute";
import Payment from "./pages/Payment";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/:id" element={<MovieDetails />} />
        <Route path="/:id/:theater" element={<Theater />}>
          <Route path="/:id/:theater/:screen/signup" element={<Signup />} />
          <Route path="/:id/:theater/:screen/signin" element={<Signin />} />
        </Route>
        <Route
          path="/:id/:screen/booking"
          element={
            <ProtectRoute>
              <Booking />
            </ProtectRoute>
          }
        />
        <Route path="/:id/:screen/:bookingId" element={<Payment />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
