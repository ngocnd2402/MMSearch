import Image from "next/image";

export const images = [
    {
        id: 1,
        title: "UIT",
        src: "/uit.svg"
    },
    {
        id: 2,
        title: "CS",
        src: "/cs.svg"
    },
    {
        id: 3,
        title: "MMLab",
        src: "/mmlab.png"
    }
]

const Logos = () => {
    return (
        <div className="flex gap-4 py-2 px-4 bg-white rounded-full mt-1">
            {images.map(({ id, title, src }) => (
                <Image src={src} key={id} alt={title} height={24} width={32} style={{objectFit: "contain"}}/>
            ))}
        </div>
    )
}

export default Logos;