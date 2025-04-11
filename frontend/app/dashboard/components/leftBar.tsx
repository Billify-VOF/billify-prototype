import { useState } from "react";
import { LiaFileInvoiceSolid } from "react-icons/lia";
import { IoSettingsOutline } from "react-icons/io5";
import { LiaWalletSolid } from "react-icons/lia";
import { IoShieldCheckmarkOutline } from "react-icons/io5";
import { HiOutlineSupport, HiOutlineChartPie } from "react-icons/hi";
import logo from '../../../assets/images/logo.png'

const LeftBar = () => {
    const [activeItem, setActiveItem] = useState("Dashboard");

    const menuItems = [
        { label: "Dashboard", icon: HiOutlineChartPie },
        { label: "Invoices", icon: LiaFileInvoiceSolid },
        { label: "Wallets", icon: LiaWalletSolid },
        { label: "Settings", icon: IoSettingsOutline },
        { label: "Privecy Policy", icon: IoShieldCheckmarkOutline },
        { label: "Help & Support", icon: HiOutlineSupport },
    ];

    return (
        <div className="flex w-24 lg:w-80  flex-col border-r-2 border-gray-200 bg-white py-6 px-2 lg:px-6">
            <div className="flex text-xl font-semibold text-gray-700 justify-center lg:justify-start">
                <img src={logo.src} alt="avatar"></img>

            </div>
            <div className="mt-10 flex flex-col justify-center gap-y-2">
                {menuItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = activeItem === item.label;
                    return (
                        <div
                            key={item.label}
                            onClick={() => setActiveItem(item.label)}
                            className={`flex flex-row px-2 py-4 gap-x-3 rounded-xl cursor-pointer hover:bg-blue-50 transition-all justify-center lg:justify-start ${isActive ? "bg-blue-500/5 " : ""
                                }`}
                        >
                            <Icon size={24} className={`${isActive ? "text-blue-600" : "text-gray-600"}`} />
                            <span className={`${isActive ? "font-bold text-gray-800 hidden lg:block" : "text-gray-700 hidden lg:block"}`}>
                                {item.label}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default LeftBar;
