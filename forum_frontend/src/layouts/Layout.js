import React from "react";
import { Outlet } from "react-router-dom";

export function Layout() {
  return (
    <> 
        <div className="App container">
            <Outlet />
        </div>
    </>
  );
}

export default Layout
