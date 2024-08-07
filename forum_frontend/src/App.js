import "./App.css";
import "bootstrap/dist/css/bootstrap.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./layouts/Layout/Layout";
import Home from "./components/Home/Home";
import Login from "./components/Authorization/Login";
import StartupsList from "./components/StartupsList/StartupsList";

function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="login" element={<Login />} />
            <Route path="startups" element={<StartupsList />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
