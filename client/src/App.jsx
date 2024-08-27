import { BrowserRouter, Routes } from "react-router-dom";

import Homepage from "./pages/Homepage";
import MovieDetails from "./pages/MovieDetails";
import { Route } from "react-router-dom";
import Theater from "./pages/Theater";
import Signup from "./pages/Signup";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/:id" element={<MovieDetails />} />
        <Route path="/:id/:theater" element={<Theater />}>
          <Route path="/:id/:theater/signup" element={<Signup />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
