import "./App.css";
import "bootstrap/dist/css/bootstrap.css";
import { Routes, Route } from "react-router-dom";
import Layout from "./layouts/Layout";
import Home from "./components/Home/Home";
import Login from "./components/Authorization/Login";
import StartupsList from "./components/StartupsList/StartupsList";
import RoomsList from "./components/RoomsList/RoomsList";

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="login" element={<Login />} />
          <Route path="startups" element={<StartupsList />} />
          <Route path="inbox" element={<RoomsList/>} />
        </Route>
      </Routes>
    </>
  );
}

export default App;
