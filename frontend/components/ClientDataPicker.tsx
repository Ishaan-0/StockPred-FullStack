// ClientDatePicker.tsx
"use client";

import { useState, useEffect, ReactElement } from "react";
import { DatePicker, DatePickerProps } from "@mui/x-date-pickers";
import { Dayjs } from "dayjs";

// Define props type for the component
type ClientDatePickerProps = DatePickerProps;

export default function ClientDatePicker(
  props: ClientDatePickerProps,
): ReactElement {
  const [mounted, setMounted] = useState<boolean>(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div style={{ height: 56 }} />;
  }

  return <DatePicker {...props} />;
}
