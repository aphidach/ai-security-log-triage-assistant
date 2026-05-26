import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Slot } from "radix-ui"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "group/button inline-flex shrink-0 cursor-pointer items-center justify-center rounded-[6px] border border-transparent bg-clip-padding text-sm font-semibold whitespace-nowrap transition-all outline-none select-none focus-visible:border-[#AE4DFF] focus-visible:ring-3 focus-visible:ring-[#AE4DFF]/30 active:not-aria-[haspopup]:translate-y-px disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        default: "bg-[#AE4DFF] text-white hover:bg-[#8B2FE0]",
        outline:
          "border-[#35363D] bg-transparent text-[#EAEAF0] hover:border-[#4A4B54] hover:bg-[#27282F] aria-expanded:bg-[#27282F] aria-expanded:text-[#EAEAF0]",
        secondary:
          "border-[#35363D] bg-[#27282F] text-[#EAEAF0] hover:bg-[#30313A] aria-expanded:bg-[#30313A] aria-expanded:text-[#EAEAF0]",
        ghost:
          "text-[#EAEAF0] hover:bg-[#27282F] hover:text-[#EAEAF0] aria-expanded:bg-[#27282F] aria-expanded:text-[#EAEAF0]",
        destructive:
          "bg-[#EF4444] text-white hover:bg-[#DC2626] focus-visible:border-[#EF4444] focus-visible:ring-[#EF4444]/25",
        link: "text-[#4F8EF7] underline-offset-4 hover:underline",
      },
      size: {
        default:
          "h-9 gap-2 px-4 has-data-[icon=inline-end]:pr-3 has-data-[icon=inline-start]:pl-3",
        xs: "h-7 gap-1 rounded-[6px] px-2 text-xs in-data-[slot=button-group]:rounded-[6px] has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 [&_svg:not([class*='size-'])]:size-3",
        sm: "h-8 gap-1.5 rounded-[6px] px-3 text-[0.8rem] in-data-[slot=button-group]:rounded-[6px] has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2 [&_svg:not([class*='size-'])]:size-3.5",
        lg: "h-11 gap-2 px-4 has-data-[icon=inline-end]:pr-3 has-data-[icon=inline-start]:pl-3",
        icon: "size-10",
        "icon-xs":
          "size-7 rounded-[6px] in-data-[slot=button-group]:rounded-[6px] [&_svg:not([class*='size-'])]:size-3",
        "icon-sm":
          "size-8 rounded-[6px] in-data-[slot=button-group]:rounded-[6px]",
        "icon-lg": "size-11",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot.Root : "button"

  return (
    <Comp
      data-slot="button"
      data-variant={variant}
      data-size={size}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
