module traffic_light_controller ( clk, reset, north_south, east_west );
  output [2:0] north_south;
  output [2:0] east_west;
  input clk, reset;
  wire   N80, N81, N82, N83, N85, N96, n40, n41, n42, n45, n46, n47, n48, n49,
         n50, n51, n52, n53, n54, n55, n56, n57, n58, n59, n60, n61, n62, n63,
         n64, n65, n66, n67, n68, n69, n70, n71, n72, n73, n74, n75, n76, n77,
         n78, n79, n80, n81, n82, n83;
  wire   [2:0] traffic_light_state;
  assign north_south[0] = N85;
  assign east_west[0] = N96; 

  DFF_X1 \counter_reg[0]  ( .D(N80), .CK(clk), .Q(n81), .QN(n50) );
  DFF_X1 \counter_reg[1]  ( .D(N81), .CK(clk), .Q(n82), .QN(n46) );
  DFF_X1 \counter_reg[2]  ( .D(N82), .CK(clk), .QN(n45) );
  DFF_X1 \counter_reg[3]  ( .D(N83), .CK(clk), .Q(n83) );
  DFF_X1 \traffic_light_state_reg[0]  ( .D(n42), .CK(clk), .Q(
        traffic_light_state[0]), .QN(n48) );
  DFF_X1 \traffic_light_state_reg[2]  ( .D(n41), .CK(clk), .Q(
        traffic_light_state[2]), .QN(n47) );
  DFF_X1 \traffic_light_state_reg[1]  ( .D(n40), .CK(clk), .Q(
        traffic_light_state[1]), .QN(n49) );
  NAND2_X1 U51 ( .A1(n51), .A2(n52), .ZN(n42) ); 
  INV_X1 U52 ( .A(N96), .ZN(n52) );
  MUX2_X1 U53 ( .A(n53), .B(n54), .S(traffic_light_state[0]), .Z(n51) );
  NOR2_X1 U54 ( .A1(n53), .A2(n55), .ZN(n54) );
  OAI22_X1 U55 ( .A1(n47), .A2(n56), .B1(reset), .B2(n57), .ZN(n41) );
  AOI21_X1 U56 ( .B1(n58), .B2(n59), .A(N96), .ZN(n57) );
  NOR2_X1 U57 ( .A1(traffic_light_state[0]), .A2(n53), .ZN(n58) );
  OAI21_X1 U58 ( .B1(n53), .B2(n60), .A(n61), .ZN(n40) );
  OAI21_X1 U59 ( .B1(n53), .B2(n48), .A(traffic_light_state[1]), .ZN(n61) );
  AOI211_X1 U60 ( .C1(traffic_light_state[2]), .C2(n48), .A(n55), .B(
        north_south[1]), .ZN(n60) );
  OR2_X1 U61 ( .A1(reset), .A2(east_west[1]), .ZN(n55) );
  INV_X1 U62 ( .A(n56), .ZN(n53) );
  OAI211_X1 U63 ( .C1(n62), .C2(n63), .A(n64), .B(n65), .ZN(n56) );
  AOI211_X1 U64 ( .C1(traffic_light_state[2]), .C2(n66), .A(reset), .B(n67), 
        .ZN(n65) );
  AND3_X1 U65 ( .A1(n83), .A2(n68), .A3(N85), .ZN(n67) );
  OAI21_X1 U66 ( .B1(n49), .B2(n69), .A(traffic_light_state[0]), .ZN(n66) );
  AOI22_X1 U67 ( .A1(east_west[1]), .A2(n70), .B1(n59), .B2(n81), .ZN(n64) );
  INV_X1 U68 ( .A(north_south[1]), .ZN(n63) );
  NOR2_X1 U69 ( .A1(n71), .A2(n72), .ZN(N83) );
  XNOR2_X1 U70 ( .A(n83), .B(n68), .ZN(n71) );
  AOI211_X1 U71 ( .C1(n45), .C2(n62), .A(n72), .B(n68), .ZN(N82) );
  NOR2_X1 U72 ( .A1(n45), .A2(n62), .ZN(n68) );
  NOR2_X1 U73 ( .A1(n73), .A2(n72), .ZN(N81) );
  INV_X1 U74 ( .A(n74), .ZN(n72) );
  AOI21_X1 U75 ( .B1(n75), .B2(n76), .A(reset), .ZN(n74) );
  NAND2_X1 U76 ( .A1(n50), .A2(n59), .ZN(n75) );
  AOI21_X1 U78 ( .B1(n81), .B2(n46), .A(n70), .ZN(n73) );
  AOI211_X1 U79 ( .C1(n76), .C2(n77), .A(reset), .B(n81), .ZN(N80) );
  NAND2_X1 U80 ( .A1(traffic_light_state[1]), .A2(n47), .ZN(n77) );
  AOI211_X1 U81 ( .C1(n62), .C2(north_south[1]), .A(N85), .B(n78), .ZN(n76) );
  INV_X1 U82 ( .A(n79), .ZN(n78) );
  AOI22_X1 U83 ( .A1(N96), .A2(n69), .B1(east_west[1]), .B2(n80), .ZN(n79) );
  INV_X1 U84 ( .A(n70), .ZN(n80) );
  NOR2_X1 U85 ( .A1(n46), .A2(n81), .ZN(n70) );
  NOR2_X1 U86 ( .A1(east_west[2]), .A2(traffic_light_state[1]), .ZN(
        east_west[1]) );
  NAND4_X1 U87 ( .A1(n83), .A2(n46), .A3(n45), .A4(n50), .ZN(n69) );
  NOR2_X1 U88 ( .A1(n49), .A2(east_west[2]), .ZN(N96) );
  NAND2_X1 U89 ( .A1(traffic_light_state[2]), .A2(traffic_light_state[0]), 
        .ZN(east_west[2]) );
  NOR2_X1 U90 ( .A1(north_south[2]), .A2(traffic_light_state[0]), .ZN(N85) );
  NOR2_X1 U91 ( .A1(n48), .A2(north_south[2]), .ZN(north_south[1]) );
  NAND2_X1 U92 ( .A1(n47), .A2(n49), .ZN(north_south[2]) );
  NAND2_X1 U93 ( .A1(n81), .A2(n82), .ZN(n62) );
endmodule




