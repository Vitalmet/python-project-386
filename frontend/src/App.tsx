import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { AdminBookings } from "./pages/AdminBookings";
import { AdminEventTypes } from "./pages/AdminEventTypes";
import { BookingForm } from "./pages/BookingForm";
import { BookingSuccess } from "./pages/BookingSuccess";
import { Calendar } from "./pages/Calendar";
import { Home } from "./pages/Home";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/event-types/:id" element={<Calendar />} />
          <Route path="/event-types/:id/book" element={<BookingForm />} />
          <Route path="/bookings/:id" element={<BookingSuccess />} />
          <Route path="/admin/event-types" element={<AdminEventTypes />} />
          <Route path="/admin/bookings" element={<AdminBookings />} />
          <Route path="*" element={<Home />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
